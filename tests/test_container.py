import importlib
import queue
from unittest import TestCase
from unittest.mock import patch, MagicMock, call

import app.container
from app.config import MqttConfig, SensorsConfig
from app.mqtt_client import MqttClient
from app.services import MqttService, SensorsService, MockSensorService


class TestAppContainer(TestCase):

    @patch('app.container.providers.Singleton')
    def test_container_providers(self, mock_singleton):
        mock_mqtt_config_instance = MagicMock()
        mock_sensors_config_instance = MagicMock()
        mock_mqtt_client_instance = MagicMock()
        mock_mqtt_service_instance = MagicMock()
        mock_sensors_service_instance = MagicMock()
        mock_mock_sensor_service_instance = MagicMock()
        mock_queue_service_instance = MagicMock()

        mock_singleton.side_effect = [
            mock_queue_service_instance,
            mock_mqtt_config_instance,
            mock_sensors_config_instance,
            mock_mqtt_client_instance,
            mock_mqtt_service_instance,
            mock_sensors_service_instance,
            mock_mock_sensor_service_instance,
        ]

        importlib.reload(app.container)
        from app.container import AppContainer

        self.assertEqual(mock_singleton.call_count, 7)
        expected_calls = [
            call(queue.Queue),
            call(MqttConfig),
            call(SensorsConfig.load_from_env),
            call(MqttClient, config=mock_singleton.return_value),
            call(MqttService, mock_singleton.return_value, mock_singleton.return_value),
            call(SensorsService, mock_singleton.return_value, mock_singleton.return_value),
            call(MockSensorService, mock_singleton.return_value),
        ]
