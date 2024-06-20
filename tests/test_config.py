import unittest
from unittest import TestCase
from unittest.mock import patch

from src.config import MqttConfig, SensorsConfig


class TestConfig(TestCase):

    @patch.dict('os.environ', {
        'MQTT_BROKER_URL': 'mqtt://tests-broker',
        'MQTT_BROKER_PORT': '1883',
        'MQTT_USERNAME': 'test_user',
        'MQTT_PASSWORD': 'test_password'
    })
    def test_mqtt_config_from_env(self):
        config = MqttConfig()
        self.assertEqual(config.broker_url, 'mqtt://tests-broker')
        self.assertEqual(config.broker_port, 1883)
        self.assertEqual(config.username, 'test_user')
        self.assertEqual(config.password, 'test_password')

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


if __name__ == '__main__':
    unittest.main()
