import importlib
import queue
import injector
from unittest import TestCase
from unittest.mock import patch, MagicMock

import app.container
from app.models import MqttConfig, SensorsConfig, RfidConfig
from app.mqtt_client import MqttClient
from app.services import MqttService, SensorsService, MockSensorService


class TestAppContainer(TestCase):

    @patch("app.container._load_configs")
    @patch("app.container.MqttClient")
    @patch("app.container.MqttService")
    @patch("app.container.SensorsService")
    @patch("app.container.MockSensorService")
    def test_container_bindings(
        self,
        mock_mock_sensor_service,
        mock_sensors_service,
        mock_mqtt_service,
        mock_mqtt_client,
        mock_load_configs,
    ):
        # prepare the values that _load_configs should return
        mqtt_cfg = MagicMock(spec=MqttConfig)
        sensors_cfg = MagicMock(spec=SensorsConfig)
        rfid_cfg = MagicMock(spec=RfidConfig)
        mock_load_configs.return_value = (mqtt_cfg, sensors_cfg, rfid_cfg)

        inj = injector.Injector([app.container.AppModule()])

        # queue is a singleton
        q1 = inj.get(queue.Queue)
        q2 = inj.get(queue.Queue)
        self.assertIs(q1, q2)

        # configuration objects come from _load_configs
        self.assertIs(inj.get(MqttConfig), mqtt_cfg)
        self.assertIs(inj.get(SensorsConfig), sensors_cfg)
        self.assertIs(inj.get(RfidConfig), rfid_cfg)

        # ensure the provider methods built the rest of the graph
        mqtt_client_obj = inj.get(MqttClient)
        mock_mqtt_client.assert_called_once_with(mqtt_cfg)

        mqtt_service_obj = inj.get(MqttService)
        mock_mqtt_service.assert_called_once_with(mqtt_client_obj)

        sensors_service_obj = inj.get(SensorsService)
        mock_sensors_service.assert_called_once_with(sensors_cfg, mqtt_service_obj)

        mock_sensor_obj = inj.get(MockSensorService)
        mock_mock_sensor_service.assert_called_once_with(sensors_service_obj)
