import os
from pathlib import Path
from typing import Dict

from pydantic import Field
from pydantic_settings import BaseSettings


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

    @classmethod
    def is_real_board(cls):
        pin_factory = os.environ.get("GPIOZERO_PIN_FACTORY")
        return pin_factory != "mock"

    class Config:
        env_prefix = 'SENSOR_'


def get_config_path():
    return Path.home() / ".PiAlarmAdapter" / "config.ini"
