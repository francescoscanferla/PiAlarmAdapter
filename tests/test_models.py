import os
from unittest import TestCase
from unittest.mock import patch

from parameterized import parameterized

from app.models import MessageModel, SensorsConfig


class TestMessageModel(TestCase):

    def test_to_dict(self):
        status = "test_status"
        name = "test_name"
        pin = 5
        qos = 1

        expected = {
            "status": status,
            "pin": pin,
            "name": name,
            "qos": qos
        }
        message = MessageModel(status, pin, name, qos)
        actual = message.to_dict()

        assert actual == expected

    @parameterized.expand([
        ({"GPIOZERO_PIN_FACTORY": "mock"}, False),
        ({"GPIOZERO_PIN_FACTORY": "real"}, True)
    ])
    @patch.dict(os.environ, clear=True)
    def test_is_real_board(self, env_vars, expected):
        os.environ.update(env_vars)
        actual = SensorsConfig.is_real_board()
        self.assertEqual(actual, expected)
