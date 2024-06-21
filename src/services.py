from typing import Dict

from gpiozero import Button

from src.config import SensorsConfig
from src.mqtt_client import MqttClient


class MqttService:
    topic_prefix = "alarm/"

    def __init__(self, mqtt_client: MqttClient):
        self.mqtt_client = mqtt_client

    def _get_topic(self, sub_topic: str):
        return f"{self.topic_prefix}{sub_topic}"

    def publish_message(self, topic, message) -> None:
        self.mqtt_client.publish_message(self._get_topic(topic), message)

    def connect(self):
        self.mqtt_client.connect()

    def disconnect(self) -> None:
        self.mqtt_client.disconnect()


class SensorsService:
    sensors: Dict[int, Button] = {}

    def __init__(self, sensors_config: SensorsConfig):
        self.config = sensors_config

    @classmethod
    def on_close(cls, btn):
        print("Close: ", btn)

    @classmethod
    def on_open(cls, btn):
        print("Open: ", btn)

    def init_sensors(self):
        for k, v in self.config.sensors.items():
            button = Button(k)
            button.when_activated = SensorsService.on_close
            button.when_deactivated = SensorsService.on_open
            self.sensors[k] = button
