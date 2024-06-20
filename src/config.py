import os
from typing import Dict

from pydantic import Field
from pydantic_settings import BaseSettings


class MqttConfig(BaseSettings):
    broker_url: str
    broker_port: int
    username: str
    password: str

    class Config:
        env_prefix = 'MQTT_'


class SensorsConfig(BaseSettings):
    sensors: Dict[int, str] = Field(default_factory=dict)

    @classmethod
    def load_from_env(cls):
        sensors = {}
        for key, value in os.environ.items():
            if key.startswith(cls.Config.env_prefix):
                sensor_name = key[len(cls.Config.env_prefix):].lower()
                sensors[int(value)] = sensor_name
        return cls(sensors=sensors)

    class Config:
        env_prefix = 'SENSOR_'
