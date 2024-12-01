import logging

import paho.mqtt.client as mqtt

from app.models import MqttConfig


class MqttClient:

    def __init__(self, config: MqttConfig) -> None:
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.username_pw_set(config.username, config.password)

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        self.logger.info("Connected to broker: %s:%s with code %s",
                         self.config.address, self.config.port, reason_code)

    def connect(self):
        self.logger.info(
            "Attempting to connect to %s:%s",
            self.config.address,
            self.config.port
        )
        self.client.connect(self.config.address, self.config.port, keepalive=120)

    def disconnect(self) -> None:
        self.logger.info(
            "Disconnecting from %s:%s",
            self.config.address,
            self.config.port
        )
        self.client.disconnect()

    def publish_message(self, topic, message) -> None:
        self.client.publish(topic, message)
        self.logger.debug("Sent message: %s to topic: %s", message, topic)
