import os
import unittest
from unittest import TestCase
from unittest.mock import patch

from parameterized import parameterized

from app.config import SensorsConfig


class TestConfig(TestCase):

    @patch.dict('os.environ', {
        'SENSOR_BEDROOM': '16',
        'SENSOR_BATHROOM': '5'
    })
    def test_sensors_config_load_from_env(self):
        expected_sensors = {
            16: 'bedroom',
            5: 'bathroom'
        }
        config = SensorsConfig.load_from_env()
        self.assertEqual(config.sensors, expected_sensors)

    @parameterized.expand([
        ({"GPIOZERO_PIN_FACTORY": "mock"}, False),
        ({"GPIOZERO_PIN_FACTORY": "real"}, True)
    ])
    @patch.dict(os.environ, clear=True)
    def test_is_real_board(self, env_vars, expected):
        os.environ.update(env_vars)
        actual = SensorsConfig.is_real_board()
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
