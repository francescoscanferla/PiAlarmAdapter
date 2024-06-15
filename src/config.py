from pydantic_settings import BaseSettings


class MqttConfig(BaseSettings):
    broker_url: str
    broker_port: int
    username: str
    password: str

    class Config:
        env_prefix = 'MQTT_'
