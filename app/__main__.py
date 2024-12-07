import logging
import os
import time

from dependency_injector.wiring import inject, Provide
from dotenv import load_dotenv

from app.config import check_config
from app.container import AppContainer
from app.services import SensorsService, MqttService, MockSensorService

load_dotenv()
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.basicConfig(
    format='%(asctime)s [%(levelname)s]: %(message)s',
    level=logging.getLevelName(log_level)
)


@inject
def main(
        mqtt_service: MqttService = Provide[AppContainer.mqtt_service],
        sensors_service: SensorsService = Provide[AppContainer.sensors_service],
        mock_sensor_service: MockSensorService = Provide[AppContainer.mock_sensor_service]
) -> None:
    mqtt_service.connect()
    sensors_service.connect_sensors()
    if not sensors_service.is_real_board():
        mock_sensor_service.start()

    check_timer: int = 0
    try:
        while True:
            check_timer += 1
            if check_timer == 10:
                sensors_service.check_sensors()
                check_timer = 0

            time.sleep(1)
    except KeyboardInterrupt:
        mqtt_service.disconnect()
        if not sensors_service.is_real_board():
            mock_sensor_service.stop()


if __name__ == "__main__":
    logging.info('PiAlarmAdapter is starting...')
    check_config()
    container = AppContainer()
    container.init_resources()
    container.wire(modules=[__name__])
    main()
