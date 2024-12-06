import queue

from dependency_injector import containers, providers

from app.config import get_config_path
from app.models import MqttConfig, SensorsConfig
from app.mqtt_client import MqttClient
from app.services import MqttService, SensorsService, MockSensorService


class AppContainer(containers.DeclarativeContainer):
    config_path = get_config_path()
    config = providers.Configuration(ini_files=[config_path])
    queue_service = providers.Singleton(queue.Queue)
    mqtt_config = providers.Singleton(
        MqttConfig,
        address=config.mqtt.address,
        port=config.mqtt.port,
        username=config.mqtt.username,
        password=config.mqtt.password
    )
    sensors_config = providers.Singleton(
        SensorsConfig,
        sensors=providers.Callable(
            lambda sensors: {int(v): k for k, v in sensors.items()},
            sensors=config.sensors
        )
    )
    mqtt_client = providers.Singleton(MqttClient, config=mqtt_config)
    mqtt_service = providers.Singleton(MqttService, mqtt_client)
    sensors_service = providers.Singleton(SensorsService, sensors_config, mqtt_service)
    mock_sensor_service = providers.Singleton(MockSensorService, sensors_service)
