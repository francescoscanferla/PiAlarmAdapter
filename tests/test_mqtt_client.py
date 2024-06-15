import unittest
from unittest import TestCase
from unittest.mock import MagicMock, patch

from src.mqtt_client import MqttClient


class TestMqttClient(TestCase):

    def setUp(self):
        self.config = MagicMock()
        self.config.username = 'testuser'
        self.config.password = 'testpassword'
        self.config.broker_url = 'mqtt://test-broker'
        self.config.broker_port = 1883

        self.mock_client = MagicMock()
        self.mock_client.username_pw_set.return_value = None
        self.mock_client.connect.return_value = None

        self.client_patcher = patch('src.mqtt_client.mqtt.Client', return_value=self.mock_client)
        self.client_patcher.start()
        self.mqtt_client = MqttClient(self.config)

    def tearDown(self):
        self.client_patcher.stop()

    def test_publish_message(self):
        topic = 'test/topic'
        message = 'Test message'

        self.mqtt_client.publish_message(topic, message)

        self.mock_client.publish.assert_called_once_with(topic, message)

    def test_disconnect(self):
        self.mqtt_client.disconnect()
        self.mock_client.disconnect.assert_called_once()


if __name__ == '__main__':
    unittest.main()
