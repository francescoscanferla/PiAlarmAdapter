from src.mqtt_client import MqttClient


class MqttService:
    topic_prefix = "alarm/"

    def __init__(self, mqtt_client: MqttClient):
        self.mqtt_client = mqtt_client

    def _get_topic(self, sub_topic: str):
        return f"{self.topic_prefix}{sub_topic}"

    def publish_message(self, topic, message) -> None:
        self.mqtt_client.publish_message(self._get_topic(topic), message)

    def disconnect(self) -> None:
        self.mqtt_client.disconnect()
