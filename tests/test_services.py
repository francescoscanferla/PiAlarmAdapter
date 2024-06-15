from unittest import TestCase
from unittest.mock import MagicMock

from src.mqtt_client import MqttClient
from src.services import MqttService


class TestMqttService(TestCase):

    def setUp(self):
        self.mqtt_client_mock = MagicMock(spec=MqttClient)
        self.mqtt_service = MqttService(self.mqtt_client_mock)

    def test_publish_message(self):
        topic = "test_topic"
        message = "test_message"
        self.mqtt_service.publish_message(topic, message)

        self.mqtt_client_mock.publish_message.assert_called_once_with("alarm/test_topic", message)

    def test_disconnect(self):
        self.mqtt_service.disconnect()
        self.mqtt_client_mock.disconnect.assert_called_once()
