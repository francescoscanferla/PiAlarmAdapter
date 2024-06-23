import json
import unittest
from queue import Queue
from typing import Dict
from unittest import TestCase
from unittest.mock import MagicMock, patch

from gpiozero import Button

from app.mqtt_client import MqttClient
from app.services import MqttService, SensorsService


class TestMqttService(TestCase):

    def setUp(self):
        self.mqtt_client_mock = MagicMock(spec=MqttClient)
        self.queue_service_mock = MagicMock(spec=Queue)
        self.mqtt_service = MqttService(self.mqtt_client_mock, self.queue_service_mock)

    def test_publish_message(self):
        topic = "test_topic"
        message = "test_message"
        self.mqtt_service.publish_message(topic, message)

        self.mqtt_client_mock.publish_message.assert_called_once_with("alarm/test_topic", message)

    @patch('threading.Thread')
    def test_connect(self, mock_thread):
        self.mqtt_service.on_message_request = MagicMock()
        self.mqtt_service.connect()
        self.mqtt_client_mock.connect.assert_called_once()
        mock_thread.assert_called_once_with(target=self.mqtt_service.on_message_request)
        thread_instance = mock_thread.return_value
        thread_instance.start.assert_called_once()

    def test_disconnect(self):
        self.mqtt_service.disconnect()
        self.mqtt_client_mock.disconnect.assert_called_once()

    def test_on_message_request(self):
        message_instance = MagicMock()
        message_instance.to_dict.return_value = {'name': 'test_message'}
        message_instance.name = 'test_message'
        self.mqtt_service.publish_message = MagicMock()
        self.queue_service_mock.get.side_effect = [message_instance, None]
        self.mqtt_service.on_message_request()

        self.mqtt_service.publish_message.assert_called_once_with('test_message', json.dumps({'name': 'test_message'}))
        self.queue_service_mock.task_done.assert_called_once()


class TestSensorsService(TestCase):

    @patch('app.services.Queue')
    @patch('app.services.SensorsConfig')
    def setUp(self, queue_service_mock, sensor_config_mock):
        self.queue_service_mock = queue_service_mock
        self.sensor_config_mock = sensor_config_mock
        self.sensors_service = SensorsService(sensors_config=sensor_config_mock, queue_service=queue_service_mock)

    def test_get_sensor_name(self):
        sensors: Dict[int, str] = {1: 'test1', 2: 'test2'}
        self.sensors_service.config.sensors = sensors
        actual = self.sensors_service._get_sensor_name(1)
        self.assertEqual(actual, 'test1')

    def test_on_close(self):
        btn: Button = MagicMock()
        btn.pin.number = 1
        self.sensors_service._get_sensor_name = MagicMock()
        self.sensors_service._get_sensor_name.return_value = "test"

        self.sensors_service.on_close(btn)

        called_arg = self.queue_service_mock.put.call_args[0][0]
        self.queue_service_mock.put.assert_called_once()
        self.assertEqual(called_arg.pin, 1)
        self.assertEqual(called_arg.status, "close")
        self.assertEqual(called_arg.name, "test")

    def test_on_open(self):
        btn: Button = MagicMock()
        btn.pin.number = 1
        self.sensors_service._get_sensor_name = MagicMock()
        self.sensors_service._get_sensor_name.return_value = "test"

        self.sensors_service.on_open(btn)

        called_arg = self.queue_service_mock.put.call_args[0][0]
        self.queue_service_mock.put.assert_called_once()
        self.assertEqual(called_arg.pin, 1)
        self.assertEqual(called_arg.status, "open")
        self.assertEqual(called_arg.name, "test")

    @patch('app.services.Button')
    def test_connect_sensors(self, mock_button):
        config = MagicMock()
        queue_mock = MagicMock(Queue)
        config.sensors = {1: 'value1', 2: 'value2'}
        sensors_service = SensorsService(sensors_config=config, queue_service=queue_mock)
        sensors_service.connect_sensors()
        self.assertEqual(len(sensors_service.sensors), len(config.sensors))
        expected_calls = [unittest.mock.call(1), unittest.mock.call(2)]
        mock_button.assert_has_calls(expected_calls, any_order=True)


if __name__ == '__main__':
    unittest.main()
