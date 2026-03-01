import os
from typing import Dict

from pydantic import BaseModel, Field, field_validator


class MessageModel:
    status: str
    pin: int
    name: str
    qos: int

    def __init__(self, status, pin, name, qos=0):
        self.status = status
        self.pin = pin
        self.name = name
        self.qos = qos

    def to_dict(self):
        return {
            "status": self.status,
            "pin": self.pin,
            "name": self.name,
            "qos": self.qos
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
        return os.environ.get("GPIO_MOCK", "false").lower() != "true"


class RfidSensorConfig(BaseModel):
    cs_pin: int
    rst_pin: int


class RfidConfig(BaseModel):
    sensors: Dict[str, RfidSensorConfig]

    @field_validator("sensors", mode="before")
    def parse_sensors(cls, value: dict):
        parsed_sensors = {}
        for sensor_name, pins in value.items():
            cs_pin, rst_pin = map(int, pins.split(","))
            parsed_sensors[sensor_name] = {"cs_pin": cs_pin, "rst_pin": rst_pin}
        return parsed_sensors
