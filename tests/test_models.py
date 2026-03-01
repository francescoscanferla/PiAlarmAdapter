import os
import unittest
from unittest import TestCase
from unittest.mock import patch
from parameterized import parameterized
from app.models import RfidConfig, RfidSensorConfig, MessageModel, SensorsConfig


class TestMessageModel(TestCase):

    def test_to_dict(self):
        message = MessageModel("open", 5, "test", 1)
        expected = {"status": "open", "pin": 5, "name": "test", "qos": 1}
        self.assertEqual(message.to_dict(), expected)

    def test_defaults_qos(self):
        message = MessageModel("open", 5, "test")
        self.assertEqual(message.qos, 0)


@parameterized.expand(
    [
        ({"GPIO_MOCK": "true"}, False),
        ({"GPIO_MOCK": "false"}, True),
        ({}, False),  # Assente = non mock = reale
    ]
)
class TestSensorsConfigIsRealBoard(TestCase):

    def test_isrealboard(self, env_vars, expected):
        with patch.dict(os.environ, env_vars, clear=True):
            actual = SensorsConfig.isrealboard
            self.assertEqual(actual, expected)


class TestRfidConfig(TestCase):

    def test_parse_sensors(self):
        input_data = {"sensors": {"sensor1": "10,20", "sensor2": "30,40"}}
        config = RfidConfig(**input_data)
        expected = {
            "sensor1": RfidSensorConfig(cs_pin=10, rst_pin=20),
            "sensor2": RfidSensorConfig(cs_pin=30, rst_pin=40),
        }
        self.assertEqual(config.sensors, expected)


if __name__ == "__main__":
    unittest.main()
