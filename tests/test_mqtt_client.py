import unittest
from unittest import TestCase
from unittest.mock import MagicMock, patch

from app.mqtt_client import MqttClient


class TestMqttClient(TestCase):

    @patch('app.mqtt_client.logging.getLogger')
    def setUp(self, get_logger_mock):
        self.logger_mock = MagicMock()
        get_logger_mock.return_value = self.logger_mock
        self.config = MagicMock()
        self.config.username = 'test_user'
        self.config.password = 'test_password'
        self.config.broker_url = 'mqtt://test-broker'
        self.config.broker_port = 1883

        self.mock_client = MagicMock()
        self.mock_client.username_pw_set.return_value = None
        self.mock_client.connect.return_value = None

        self.client_patcher = patch('app.mqtt_client.mqtt.Client', return_value=self.mock_client)
        self.client_patcher.start()
        self.mqtt_client = MqttClient(self.config)

    def tearDown(self):
        self.client_patcher.stop()

    def test_on_connect(self):
        self.mqtt_client._on_connect(None, None, None, 0, None)
        self.logger_mock.info.assert_called_once_with(
            "Connected to broker: %s:%s with code %s",
            'mqtt://test-broker', 1883, 0
        )

    def test_connect(self):
        self.mqtt_client.connect()
        self.mock_client.connect.assert_called_once_with('mqtt://test-broker', 1883)

    def test_disconnect(self):
        self.mqtt_client.disconnect()
        self.mock_client.disconnect.assert_called_once()

    def test_publish_message(self):
        topic = 'test/topic'
        message = 'Test message'

        self.mqtt_client.publish_message(topic, message)

        self.mock_client.publish.assert_called_once_with(topic, message)


if __name__ == '__main__':
    unittest.main()
