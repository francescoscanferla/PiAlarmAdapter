import json
import logging
import threading
import time

try:
    import gpiod

    GPIOD_AVAILABLE = True
except ImportError:
    GPIOD_AVAILABLE = False

from collections import defaultdict
from app.models import MessageModel, SensorsConfig, RfidConfig
from app.mqtt_client import MqttClient


class MqttService:
    topic_prefix = "alarm/"
    topic_suffix = "/status"

    def __init__(self, mqtt_client: MqttClient):
        self.logger = logging.getLogger(__name__)
        self.mqtt_client = mqtt_client

    def _get_topic(self, sub_topic: str) -> str:
        return f"{self.topic_prefix}{sub_topic}"

    def publish_message(self, msg) -> None:
        msg_str = msg.to_dict()
        topic = msg.name + self.topic_suffix
        self.logger.debug(f"Message requests for: {json.dumps(msg_str)}")
        self.mqtt_client.publish_message(self._get_topic(topic), msg.status, msg.qos)

    def connect(self) -> None:
        self.mqtt_client.connect()

    def disconnect(self) -> None:
        self.mqtt_client.disconnect()


class SensorsService:

    def __init__(self, sensors_config: SensorsConfig, mqtt_service: MqttService):
        self.logger = logging.getLogger(__name__)
        self.config = sensors_config
        self.mqtt_service = mqtt_service
        self.chip = None
        self.lines = {}
        self.last_values = {}
        self.last_change = defaultdict(float)
        self.DEBOUNCE_TIME = 0.05

    def name_from_pin(self, pin: int) -> str:
        return self.config.sensors[pin]

    @property
    def is_real_board(self) -> bool:
        return self.config.is_real_board

    def connect_sensors(self):
        if not self.is_real_board:
            self.logger.info("Mock mode enabled. Real GPIO excluded")
            return
        if not GPIOD_AVAILABLE:
            self.logger.warning("gpiod not available. Force use mock.")
            return
        try:
            self.chip = gpiod.Chip("gpiochip0")
            for pin_str, name in self.config.sensors.items():
                pin = int(pin_str)
                line = self.chip.get_line(pin)
                line.request(
                    consumer=name,
                    type=gpiod.LINE_REQ_DIR_IN,
                    flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP,
                )
                self.lines[pin] = (line, name)
                self.last_values[pin] = line.get_value()
                self.logger.info(f"Sensor {name} on GPIO {pin} connected.")
        except Exception as e:
            self.logger.error(f"Error on GPIO: {e}. Try to use isrealboard=false.")

    def check_sensors(self):
        if not self.lines:
            return
        for pin, (line, name) in self.lines.items():
            value = line.get_value()
            now = time.time()
            if (
                value != self.last_values.get(pin, -1)
                and now - self.last_change[pin] > self.DEBOUNCE_TIME
            ):
                status = "closed" if value == 0 else "open"  # 0=chiuso (pull-up)
                self.mqtt_service.publish_message(
                    MessageModel(status=status, pin=pin, name=name, qos=2)
                )
                self.logger.info(f"{name} (GPIO{pin}): {status}")
                self.last_values[pin] = value
                self.last_change[pin] = now

    def close(self):
        for line, _ in self.lines.values():
            line.release()
        if self.chip:
            self.chip.close()


class RfidService:

    def __init__(self, rfid_config: RfidConfig):
        self.config = rfid_config

    def connect_sensors(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("RfidService: connect_sensors (not yet implemented)")


class MockSensorService:
    def __init__(self, sensors_service: SensorsService):
        self.thread = None
        self.interval = 30
        self.sensors_service = sensors_service
        self.logger = logging.getLogger(__name__)
        self.stop_event = threading.Event()
        self.mock_states = {pin: 1 for pin in sensors_service.config.sensors.keys()}

    def _toggle_state(self):
        time.sleep(10)
        while not self.stop_event.is_set():
            for pin, name in self.sensors_service.config.sensors.items():
                new_value = 0 if self.mock_states[pin] == 1 else 1
                self.mock_states[pin] = new_value
                status = "closed" if new_value == 0 else "open"
                self.logger.debug(f"[MOCK] {name} GPIO{pin}: {status}")
                self.sensors_service.mqtt_service.publish_message(
                    MessageModel(status=status, pin=pin, name=name, qos=2)
                )
            time.sleep(self.interval)

    def start(self):
        self.thread = threading.Thread(target=self._toggle_state, daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        self.thread.join()
