import logging
import os
import time

from dependency_injector.wiring import inject, Provide
from dotenv import load_dotenv

from app.config import SensorsConfig
from app.container import AppContainer
from app.services import SensorsService, MqttService, MockSensorService

load_dotenv()
log_level = os.environ.get('LOG_LEVEL')
logging.basicConfig(format='%(asctime)s [%(levelname)s]: %(message)s', level=logging.getLevelName(log_level))


@inject
def main(
        mqtt_service: MqttService = Provide[AppContainer.mqtt_service],
        sensors_config: SensorsConfig = Provide[AppContainer.sensors_config],
        sensors_service: SensorsService = Provide[AppContainer.sensors_service],
        mock_sensor_service: MockSensorService = Provide[AppContainer.mock_sensor_service]
) -> None:
    mqtt_service.connect()
    sensors_service.connect_sensors()
    if not sensors_config.is_real_board():
        mock_sensor_service.start()

    try:
        logging.info('PiAlarmAdapter started')
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        mqtt_service.disconnect()
        if not sensors_config.is_real_board():
            mock_sensor_service.stop()


if __name__ == "__main__":
    logging.info('PiAlarmAdapter is starting...')
    container = AppContainer()
    container.init_resources()
    container.wire(modules=[__name__])
    main()
