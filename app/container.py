import queue

from dependency_injector import containers, providers

from src.config import MqttConfig, SensorsConfig
from src.mqtt_client import MqttClient
from src.services import MqttService, SensorsService, MockSensorService


class AppContainer(containers.DeclarativeContainer):
    queue_service = providers.Singleton(queue.Queue)
    mqtt_config = providers.Singleton(MqttConfig)
    sensors_config = providers.Singleton(SensorsConfig.load_from_env)
    mqtt_client = providers.Singleton(MqttClient, config=mqtt_config)
    mqtt_service = providers.Singleton(MqttService, mqtt_client, queue_service)
    sensors_service = providers.Singleton(SensorsService, sensors_config, queue_service)
    mock_sensor_service = providers.Singleton(MockSensorService, sensors_service)
