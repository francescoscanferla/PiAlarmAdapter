import os
import unittest
import threading
from unittest import TestCase
from unittest.mock import MagicMock, patch, call
from app.models import MessageModel
from app.mqtt_client import MqttClient
from app.services import MqttService, SensorsService, MockSensorService


class TestMqttService(TestCase):

    def setUp(self):
        self.mqtt_client_mock = MagicMock(spec=MqttClient)
        self.mqtt_service = MqttService(self.mqtt_client_mock)

    def test_publish_message(self):
        message = MessageModel(status="open", name="test", pin=1)
        self.mqtt_service.publish_message(message)
        self.mqtt_client_mock.publish_message.assert_called_once_with(
            "alarm/test/status", "open", 0
        )

    def test_connect(self):
        self.mqtt_service.connect()
        self.mqtt_client_mock.connect.assert_called_once()

    def test_disconnect(self):
        self.mqtt_service.disconnect()
        self.mqtt_client_mock.disconnect.assert_called_once()


class TestSensorsService(TestCase):

    def setUp(self):
        self.sensors_config_mock = MagicMock()
        self.sensors_config_mock.sensors = {27: "porta", 22: "finestra"}
        self.sensors_config_mock.is_real_board = False
        self.mqtt_service_mock = MagicMock(spec=MqttService)
        self.sensors_service = SensorsService(
            sensors_config=self.sensors_config_mock, mqtt_service=self.mqtt_service_mock
        )

    def test_name_from_pin(self):
        self.sensors_service.config.sensors = {1: "test1", 2: "test2"}
        self.assertEqual(self.sensors_service.name_from_pin(1), "test1")

    def test_is_real_board_delegates_to_config(self):
        self.sensors_config_mock.is_real_board = True
        self.assertTrue(self.sensors_service.is_real_board)
        self.sensors_config_mock.is_real_board = False
        self.assertFalse(self.sensors_service.is_real_board)

    def test_connect_sensors_mock_mode_skips_gpio(self):
        self.sensors_service.connect_sensors()
        self.assertIsNone(self.sensors_service.chip)
        self.assertEqual(self.sensors_service.lines, {})

    def test_connect_sensors_gpiod_unavailable(self):
        self.sensors_config_mock.is_real_board = True
        with patch("app.services.GPIOD_AVAILABLE", False):
            self.sensors_service.connect_sensors()
        self.assertIsNone(self.sensors_service.chip)
        self.assertEqual(self.sensors_service.lines, {})

    def test_check_sensors_no_lines_does_nothing(self):
        self.sensors_service.lines = {}
        self.sensors_service.check_sensors()
        self.mqtt_service_mock.publish_message.assert_not_called()

    def test_check_sensors_publishes_on_change(self):
        line_mock = MagicMock()
        line_mock.get_value.return_value = 0  # closed
        self.sensors_service.lines = {27: (line_mock, "porta")}
        self.sensors_service.last_values = {27: 1}  # era open, ora closed
        self.sensors_service.check_sensors()
        self.mqtt_service_mock.publish_message.assert_called_once()
        args = self.mqtt_service_mock.publish_message.call_args[0][0]
        self.assertEqual(args.status, "closed")
        self.assertEqual(args.pin, 27)
        self.assertEqual(args.name, "porta")

    def test_check_sensors_no_publish_without_change(self):
        line_mock = MagicMock()
        line_mock.get_value.return_value = 1  # open
        self.sensors_service.lines = {27: (line_mock, "porta")}
        self.sensors_service.last_values = {27: 1}  # stesso valore
        self.sensors_service.check_sensors()
        self.mqtt_service_mock.publish_message.assert_not_called()

    def test_check_sensors_debounce_blocks_rapid_change(self):
        import time

        line_mock = MagicMock()
        line_mock.get_value.return_value = 0
        self.sensors_service.lines = {27: (line_mock, "porta")}
        self.sensors_service.last_values = {27: 1}
        self.sensors_service.last_change[27] = time.time()  # appena cambiato
        self.sensors_service.check_sensors()
        self.mqtt_service_mock.publish_message.assert_not_called()


class TestMockSensorService(TestCase):

    def setUp(self):
        self.sensors_service_mock = MagicMock()
        self.sensors_service_mock.config.sensors = {27: "porta", 22: "finestra"}
        self.sensors_service_mock.mqtt_service = MagicMock()
        self.mock_service = MockSensorService(self.sensors_service_mock)
        self.mock_service.interval = 0.01  # Veloce per i test
        self.stop_event_mock = MagicMock()
        self.stop_event_mock.is_set.side_effect = [False, True]
        self.mock_service.stop_event = self.stop_event_mock

    def test_mock_states_initialized_from_config(self):
        self.assertIn(27, self.mock_service.mock_states)
        self.assertIn(22, self.mock_service.mock_states)
        self.assertEqual(self.mock_service.mock_states[27], 1)
        self.assertEqual(self.mock_service.mock_states[22], 1)

    def test_toggle_state_publishes_for_all_sensors(self):
        self.mock_service._toggle_state()
        publish_calls = (
            self.sensors_service_mock.mqtt_service.publish_message.call_count
        )
        # Un ciclo con 2 sensori = 2 messaggi
        self.assertEqual(publish_calls, 2)

    def test_toggle_state_changes_value(self):
        self.mock_service._toggle_state()
        self.assertEqual(self.mock_service.mock_states[27], 0)  # 1 → 0
        self.assertEqual(self.mock_service.mock_states[22], 0)

    def test_toggle_publishes_correct_status(self):
        self.mock_service._toggle_state()
        calls = self.sensors_service_mock.mqtt_service.publish_message.call_args_list
        msg_porta = calls[0][0][0]
        self.assertEqual(msg_porta.status, "closed")  # 0=closed
        self.assertEqual(msg_porta.pin, 27)
        self.assertEqual(msg_porta.name, "porta")

    @patch("threading.Thread")
    def test_start(self, mock_thread):
        thread_instance = MagicMock()
        mock_thread.return_value = thread_instance
        self.mock_service.start()
        mock_thread.assert_called_once_with(
            target=self.mock_service._toggle_state, daemon=True
        )
        thread_instance.start.assert_called_once()
        self.assertEqual(self.mock_service.thread, thread_instance)

    def test_stop(self):
        thread_mock = MagicMock()
        self.mock_service.thread = thread_mock
        self.mock_service.stop_event = MagicMock()
        self.mock_service.stop()
        self.mock_service.stop_event.set.assert_called_once()
        thread_mock.join.assert_called_once()


if __name__ == "__main__":
    unittest.main()
