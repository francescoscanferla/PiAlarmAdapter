import configparser
import unittest
from io import StringIO
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch, MagicMock

from app.config import _init_rfid_data, _init_mqtt_data, _init_sensors_data, get_config_path, setup_config, check_config


class TestConfig(TestCase):

    @patch('builtins.input', side_effect=['test.mosquitto.org', '1883', 'test_user', 'test_pass'])
    def test_init_mqtt_data(self, mock_input):
        result = _init_mqtt_data()

        expected = {
            'address': 'test.mosquitto.org',
            'port': '1883',
            'username': 'test_user',
            'password': 'test_pass'
        }

        self.assertEqual(result, expected)

    @patch('builtins.input', side_effect=['kitchen', '5', 'bedroom', '3', ''])
    def test_init_sensors_data(self, mock_input):
        result = _init_sensors_data()

        expected = {
            'kitchen': '5',
            'bedroom': '3'
        }

        self.assertEqual(result, expected)

    @patch('builtins.input', side_effect=['sensor1', '17', '19', 'sensor2', '22', '23', ''])
    def test_init_rfid_data(self, mock_input):
        result = _init_rfid_data()

        expected = {
            'sensor1': '17,19',
            'sensor2': '22,23'
        }

        self.assertEqual(result, expected)

    @patch('pathlib.Path.home')
    def test_get_config_path(self, mock_home):
        mock_home.return_value = Path('/mock/home/directory')

        expected_path = Path('/mock/home/directory/.PiAlarmAdapter/config.ini')
        result = get_config_path()

        self.assertEqual(result, expected_path)

    @patch('app.config.get_config_path')
    @patch('app.config.setup_config')
    @patch('logging.info')
    def test_config_exists(self, mock_logging, mock_setup_config, mock_get_config_path):
        mock_path = MagicMock(spec=Path)
        mock_path.exists.return_value = True
        mock_get_config_path.return_value = mock_path

        check_config()

        mock_setup_config.assert_not_called()
        mock_logging.assert_not_called()

    @patch('app.config.get_config_path')
    @patch('app.config.setup_config')
    @patch('logging.info')
    def test_config_not_exists(self, mock_logging, mock_setup_config, mock_get_config_path):
        mock_path = MagicMock(spec=Path)
        mock_path.exists.return_value = False
        mock_get_config_path.return_value = mock_path

        check_config()

        mock_setup_config.assert_called_once()
        mock_logging.assert_called_once()
        log_message = mock_logging.call_args[0][0]
        self.assertEqual("The configuration file %s does not exist. I start the setup.", log_message)

    @patch('app.config.get_config_path')
    @patch('app.config.Path.mkdir')
    @patch('app.config._init_mqtt_data')
    @patch('app.config._init_sensors_data')
    @patch('app.config._init_rfid_data')
    def test_setup_config(self, mock_init_rfid, mock_init_sensors, mock_init_mqtt, mock_mkdir, mock_get_config_path):
        mock_init_mqtt.return_value = {'address': 'localhost', 'port': '1883', 'username': 'user', 'password': 'pass'}
        mock_init_sensors.return_value = {'kitchen': '5', 'bedroom': '4'}
        mock_init_rfid.return_value = {'1': '17,19'}
        mock_get_config_path.return_value = Path('/mock/path/config.ini')

        config_output = StringIO()
        mock_open = MagicMock()
        mock_open.return_value.__enter__.return_value = config_output

        with patch('builtins.open', mock_open):
            setup_config()

        config_content = config_output.getvalue()

        config = configparser.ConfigParser()
        config.read_string(config_content)

        self.assertIn('mqtt', config)
        self.assertIn('sensors', config)
        self.assertIn('rfid', config)
        self.assertEqual(dict(config['mqtt']), mock_init_mqtt.return_value)
        self.assertEqual(dict(config['sensors']), mock_init_sensors.return_value)
        self.assertEqual(dict(config['rfid']), mock_init_rfid.return_value)


if __name__ == '__main__':
    unittest.main()
