from dependency_injector import containers, providers

from src.config import MqttConfig, SensorsConfig
from src.mqtt_client import MqttClient
from src.services import MqttService, SensorsService


class AppContainer(containers.DeclarativeContainer):
    mqtt_config = providers.Singleton(MqttConfig)
    sensors_config = providers.Singleton(SensorsConfig.load_from_env)
    mqtt_client = providers.Singleton(MqttClient, config=mqtt_config)
    mqtt_service = providers.Singleton(MqttService, mqtt_client)
    sensors_service = providers.Singleton(SensorsService, sensors_config)
