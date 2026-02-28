import queue
import configparser

import injector

from app.config import get_config_path
from app.models import MqttConfig, SensorsConfig, RfidConfig
from app.mqtt_client import MqttClient
from app.services import MqttService, SensorsService, MockSensorService, RfidService


def _load_configs():
    """
    Load the three config objects from the file indicated by
    :func:`app.config.get_config_path`.  The old
    ``providers.Configuration`` is replaced by a straightforward
    ``configparser`` read.
    """
    config_path = get_config_path()
    parser = configparser.ConfigParser()
    parser.read(config_path)

    mqtt_cfg = MqttConfig(
        address=parser["mqtt"]["address"],
        port=int(parser["mqtt"]["port"]),
        username=parser["mqtt"]["username"],
        password=parser["mqtt"]["password"],
    )
    sensors_cfg = SensorsConfig(
        sensors={int(v): k for k, v in parser["sensors"].items()}
    )
    rfid_cfg = RfidConfig(sensors=parser["rfid"])

    return mqtt_cfg, sensors_cfg, rfid_cfg


class AppModule(injector.Module):
    def __init__(self, mqtt_cfg=None, sensors_cfg=None, rfid_cfg=None):
        super().__init__()
        # tests may inject their own instances
        self._mqtt_cfg = mqtt_cfg
        self._sensors_cfg = sensors_cfg
        self._rfid_cfg = rfid_cfg

    def configure(self, binder: injector.Binder) -> None:
        # always have a queue singleton
        binder.bind(queue.Queue, to=queue.Queue, scope=injector.singleton)

        if any(x is None for x in (self._mqtt_cfg, self._sensors_cfg, self._rfid_cfg)):
            mqtt_cfg, sensors_cfg, rfid_cfg = _load_configs()
            self._mqtt_cfg = self._mqtt_cfg or mqtt_cfg
            self._sensors_cfg = self._sensors_cfg or sensors_cfg
            self._rfid_cfg = self._rfid_cfg or rfid_cfg

        binder.bind(MqttConfig, to=self._mqtt_cfg, scope=injector.singleton)
        binder.bind(SensorsConfig, to=self._sensors_cfg, scope=injector.singleton)
        binder.bind(RfidConfig, to=self._rfid_cfg, scope=injector.singleton)

    # provider methods create the remaining objects and declare the
    # dependencies they need; injector will resolve them automatically.

    @injector.singleton
    @injector.provider
    def provide_mqtt_client(self, config: MqttConfig) -> MqttClient:
        return MqttClient(config)

    @injector.singleton
    @injector.provider
    def provide_mqtt_service(self, client: MqttClient) -> MqttService:
        return MqttService(client)

    @injector.singleton
    @injector.provider
    def provide_sensors_service(
        self,
        sensors_config: SensorsConfig,
        mqtt_service: MqttService,
    ) -> SensorsService:
        return SensorsService(sensors_config, mqtt_service)

    @injector.singleton
    @injector.provider
    def provide_rfid_service(self, rfid_config: RfidConfig) -> RfidService:
        return RfidService(rfid_config)

    @injector.singleton
    @injector.provider
    def provide_mock_sensor_service(
        self,
        sensors_service: SensorsService,
    ) -> MockSensorService:
        return MockSensorService(sensors_service)
