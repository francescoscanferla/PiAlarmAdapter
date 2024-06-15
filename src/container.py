from dependency_injector import containers, providers

from src.config import MqttConfig
from src.mqtt_client import MqttClient
from src.services import MqttService


class AppContainer(containers.DeclarativeContainer):
    mqtt_config = providers.Singleton(MqttConfig)
    mqtt_client = providers.Singleton(MqttClient, config=mqtt_config)
    mqtt_service = providers.Singleton(MqttService, mqtt_client)
