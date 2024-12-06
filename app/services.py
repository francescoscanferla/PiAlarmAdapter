import json
import logging
import random
import threading
import time
from functools import partial
from typing import Dict

from gpiozero import Button

from app.models import MessageModel, SensorsConfig
from app.mqtt_client import MqttClient


class MqttService:
    topic_prefix = "alarm/"

    def __init__(self, mqtt_client: MqttClient):
        self.logger = logging.getLogger(__name__)
        self.mqtt_client = mqtt_client

    def _get_topic(self, sub_topic: str) -> str:
        return f"{self.topic_prefix}{sub_topic}"

    def publish_message(self, msg) -> None:
        msg_str = msg.to_dict()
        topic = msg.name + "/status"
        self.logger.debug(f"Message requests for: {json.dumps(msg_str)}")
        self.mqtt_client.publish_message(self._get_topic(topic), msg.status, 0)

    def connect(self) -> None:
        self.mqtt_client.connect()

    def disconnect(self) -> None:
        self.mqtt_client.disconnect()


class SensorsService:
    sensors: Dict[int, Button] = {}

    def __init__(
            self,
            sensors_config: SensorsConfig,
            mqtt_service: MqttService
    ):
        self.logger = logging.getLogger(__name__)
        self.config = sensors_config
        self.mqtt_service = mqtt_service

    def _get_sensor_name(self, pin: int):
        return self.config.sensors[pin]

    def on_close(self, btn: Button):
        sensor_name = self._get_sensor_name(btn.pin.number)
        logging.debug("The %s sensor is close", sensor_name)
        self.mqtt_service.publish_message(MessageModel(status="closed", pin=btn.pin.number, name=sensor_name))

    def on_open(self, btn):
        sensor_name = self._get_sensor_name(btn.pin.number)
        logging.debug("The %s sensor is open", sensor_name)
        self.mqtt_service.publish_message(MessageModel(status="open", pin=btn.pin.number, name=sensor_name))

    def connect_sensors(self):
        for k in self.config.sensors.keys():
            button = Button(k)
            button.when_pressed = partial(SensorsService.on_close, self)
            button.when_released = partial(SensorsService.on_open, self)
            self.sensors[k] = button

    def check_sensors(self):
        for pin, btn in self.sensors.items():
            sensor_name = self._get_sensor_name(pin)
            status = "closed" if btn.is_active else "open"
            self.mqtt_service.publish_message(
                MessageModel(status=status, pin=pin, name=sensor_name)
            )


class MockSensorService:
    def __init__(self, sensors_service: SensorsService):
        self._thread = None
        self.interval = 30
        self.sensors_service = sensors_service
        self.logger = logging.getLogger(__name__)
        self._stop_event = threading.Event()
        self._state = False

    def _toggle_state(self):
        time.sleep(10)
        while not self._stop_event.is_set():
            item: Dict[int, Button] = random.choice(list(self.sensors_service.sensors.items()))
            _, sensor = item
            if sensor.value == 0:
                sensor.pin.drive_low()
                self.logger.debug("Sensor on pin %s set to LOW (pressed).", sensor.pin)
            else:
                sensor.pin.drive_high()
                self.logger.debug("Sensor on pin %s set to HIGH (released).", sensor.pin)
            time.sleep(self.interval)

    def start(self):
        self._thread = threading.Thread(target=self._toggle_state)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        self._thread.join()
