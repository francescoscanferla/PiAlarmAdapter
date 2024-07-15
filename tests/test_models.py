from unittest import TestCase

from app.models import MessageModel


class TestMessageModel(TestCase):

    def test_to_dict(self):
        status = "test_status"
        name = "test_name"
        pin = 5

        expected = {
            "status": status,
            "pin": pin,
            "name": name
        }
        message = MessageModel(status, pin, name)
        actual = message.to_dict()

        assert actual == expected
