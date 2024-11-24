import json
import logging
import random
import threading
import time
from functools import partial
from queue import Queue
from typing import Dict

from gpiozero import Button

from app.models import MessageModel, SensorsConfig
from app.mqtt_client import MqttClient


class MqttService:
    topic_prefix = "alarm/"

    def __init__(self, mqtt_client: MqttClient, queue_service: Queue):
        self.logger = logging.getLogger(__name__)
        self.queue_service = queue_service
        self.mqtt_client = mqtt_client

    def _get_topic(self, sub_topic: str) -> str:
        return f"{self.topic_prefix}{sub_topic}"

    def publish_message(self, topic, message) -> None:
        self.mqtt_client.publish_message(self._get_topic(topic), message)

    def connect(self) -> None:
        self.mqtt_client.connect()
        msg_thread = threading.Thread(target=self.on_message_request)
        msg_thread.start()

    def disconnect(self) -> None:
        self.mqtt_client.disconnect()

    def on_message_request(self) -> None:
        while True:
            msg: MessageModel = self.queue_service.get()
            if msg is None:
                break
            msg_str = msg.to_dict()
            topic = msg.name + "/status"
            self.logger.debug(f"Message requests for: {json.dumps(msg_str)}")
            self.publish_message(topic, msg.status)
            self.queue_service.task_done()


class SensorsService:
    sensors: Dict[int, Button] = {}

    def __init__(self, sensors_config: SensorsConfig, queue_service: Queue):
        self.queue_service = queue_service
        self.logger = logging.getLogger(__name__)
        self.config = sensors_config

    def _get_sensor_name(self, pin: int):
        return self.config.sensors[pin]

    def on_close(self, btn: Button):
        sensor_name = self._get_sensor_name(btn.pin.number)
        logging.info("The %s sensor is close", sensor_name)
        self.queue_service.put(MessageModel(status="closed", pin=btn.pin.number, name=sensor_name))

    def on_open(self, btn):
        sensor_name = self._get_sensor_name(btn.pin.number)
        logging.info("The %s sensor is open", sensor_name)
        self.queue_service.put(MessageModel(status="open", pin=btn.pin.number, name=sensor_name))

    def connect_sensors(self):
        for k in self.config.sensors.keys():
            button = Button(k)
            button.when_pressed = partial(SensorsService.on_close, self)
            button.when_released = partial(SensorsService.on_open, self)
            self.sensors[k] = button

    def check_sensors(self):
        for pin, btn in self.sensors.items():
            sensor_name = self._get_sensor_name(btn.pin.number)
            status = "open" if btn.is_active else "closed"
            self.queue_service.put(
                MessageModel(status=status, pin=btn.pin.number, name=sensor_name)
            )


class MockSensorService:
    def __init__(self, sensors_service: SensorsService):
        self._thread = None
        self.interval = 20
        self.sensors_service = sensors_service
        self.logger = logging.getLogger(__name__)
        self._stop_event = threading.Event()
        self._state = False

    def _toggle_state(self):
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
