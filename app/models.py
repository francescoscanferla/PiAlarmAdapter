import os
from typing import Dict

from pydantic import BaseModel, Field


class MessageModel:
    status: str
    pin: int
    name: str

    def __init__(self, status, pin, name):
        self.status = status
        self.pin = pin
        self.name = name

    def to_dict(self):
        return {
            "status": self.status,
            "pin": self.pin,
            "name": self.name
        }


class MqttConfig(BaseModel):
    address: str = Field("localhost", description="Address of MQTT Broker")
    port: int = Field(1883, description="MQTT Broker port")
    username: str
    password: str


class SensorsConfig(BaseModel):
    sensors: Dict[int, str] = Field(default_factory=dict)

    @classmethod
    def is_real_board(cls):
        pin_factory = os.environ.get("GPIOZERO_PIN_FACTORY")
        return pin_factory != "mock"
