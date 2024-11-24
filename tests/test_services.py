import json
import unittest
from queue import Queue
from typing import Dict
from unittest import TestCase
from unittest.mock import MagicMock, patch

from gpiozero import Button

from app.models import SensorsConfig, MessageModel
from app.mqtt_client import MqttClient
from app.services import MqttService, SensorsService, MockSensorService


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
        message_instance.to_dict.return_value = {'name': 'test_message', 'status': 'open'}
        message_instance.name = 'test_message'
        message_instance.status = 'open'
        self.mqtt_service.publish_message = MagicMock()
        self.queue_service_mock.get.side_effect = [message_instance, None]
        self.mqtt_service.on_message_request()

        self.mqtt_service.publish_message.assert_called_once_with(
            'test_message/status',
            'open'
        )
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
        self.assertEqual(called_arg.status, "closed")
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

    def test_check_sensors(self):
        sensors_config = MagicMock(SensorsConfig)
        queue_service = MagicMock(Queue)
        _get_sensor_name = MagicMock(side_effect=lambda pin: f"Sensor-{pin}")
        sensors = {
            1: MagicMock(pin=MagicMock(number=1), is_active=True),
            2: MagicMock(pin=MagicMock(number=2), is_active=False)
        }
        sensor_service = SensorsService(sensors_config, queue_service)
        sensor_service.sensors = sensors
        sensor_service._get_sensor_name = _get_sensor_name

        sensor_service.check_sensors()
        self.assertEqual(queue_service.put.call_count, 2)
        actual_calls = [call.args[0] for call in queue_service.put.call_args_list]

        expected_calls = [
            MessageModel(status="closed", pin=1, name="Sensor-1"),
            MessageModel(status="open", pin=2, name="Sensor-2")
        ]

        for expected, actual in zip(expected_calls, actual_calls):
            self.assertEqual(expected.status, actual.status)
            self.assertEqual(expected.pin, actual.pin)
            self.assertEqual(expected.name, actual.name)

        _get_sensor_name.assert_any_call(1)
        _get_sensor_name.assert_any_call(2)


class TestMockSensorService(TestCase):

    def setUp(self):
        self.sensors_service_mock = MagicMock()
        self.sensors_service_mock.sensors = {
            17: MagicMock(pin=MagicMock(), value=0),
            18: MagicMock(pin=MagicMock(), value=1),
        }
        self.logger_mock = MagicMock()
        self.stop_event_mock = MagicMock()
        self.stop_event_mock.is_set.side_effect = [False, True]

        self.test_class = MockSensorService(
            sensors_service=self.sensors_service_mock
        )
        self.test_class.interval = 0.1
        self.test_class.logger = self.logger_mock
        self.test_class._stop_event = self.stop_event_mock

    @patch('random.choice')
    def test_toggle_state_low(self, random_choice_mock):
        random_choice_mock.side_effect = lambda x: list(self.sensors_service_mock.sensors.items())[0]

        self.test_class._toggle_state()

        self.sensors_service_mock.sensors[17].pin.drive_low.assert_called_once()
        self.sensors_service_mock.sensors[17].pin.drive_high.assert_not_called()
        self.logger_mock.debug.assert_any_call("Sensor on pin %s set to LOW (pressed).",
                                               self.sensors_service_mock.sensors[17].pin)

    @patch('random.choice')
    def test_toggle_state_high(self, random_choice_mock):
        random_choice_mock.side_effect = lambda x: list(self.sensors_service_mock.sensors.items())[1]

        self.test_class._toggle_state()

        self.sensors_service_mock.sensors[18].pin.drive_high.assert_called_once()
        self.sensors_service_mock.sensors[18].pin.drive_low.assert_not_called()
        self.logger_mock.debug.assert_any_call("Sensor on pin %s set to HIGH (released).",
                                               self.sensors_service_mock.sensors[18].pin)

    @patch('threading.Thread')
    def test_start(self, mock_thread):
        thread_instance_mock = MagicMock()
        mock_thread.return_value = thread_instance_mock

        self.test_class.start()

        mock_thread.assert_called_once_with(target=self.test_class._toggle_state)
        thread_instance_mock.start.assert_called_once()
        self.assertEqual(self.test_class._thread, thread_instance_mock)

    def test_stop(self):
        thread_instance_mock = MagicMock()
        self.test_class._thread = thread_instance_mock

        self.test_class.stop()

        self.stop_event_mock.set.assert_called_once()
        self.test_class._thread.join.assert_called_once()


if __name__ == '__main__':
    unittest.main()
