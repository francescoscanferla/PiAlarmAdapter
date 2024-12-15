import configparser
import logging
from pathlib import Path


def _init_mqtt_data():
    mqtt_address = input("Enter the address of the MQTT broker (localhost): ")
    mqtt_port = input("Enter the port number (1883): ")
    mqtt_username = input("Enter the username: ")
    mqtt_password = input("Enter the password: ")

    return {
        'address': mqtt_address,
        'port': mqtt_port,
        'username': mqtt_username,
        'password': mqtt_password
    }


def _init_sensors_data():
    data = {}
    while True:
        sensor_name = input("Enter the name of the sensor (or press Enter to finish): ")
        if not sensor_name:
            break
        sensor_value = input(f"Enter the numerical value for {sensor_name}: ")
        data[sensor_name] = sensor_value

    return data


def _init_rfid_data():
    data = {}
    while True:
        sensor_name = input("Enter the name of the rfid sensor (or press Enter to finish): ")
        cs_pin = input(f"Enter the number of CS pin of the {sensor_name}: ")
        if not cs_pin:
            break
        rst_pin = input(f"Enter the number of RST pin of the {sensor_name}: ")
        data[{sensor_name}] = f"{cs_pin},{rst_pin}"
    return data


def get_config_path():
    return Path.home() / ".PiAlarmAdapter" / "config.ini"


def check_config():
    config_path = get_config_path()
    if not config_path.exists():
        logging.info("The configuration file %s does not exist. I start the setup.", config_path)
        setup_config()


def setup_config():
    config = configparser.ConfigParser()
    config['mqtt'] = _init_mqtt_data()
    config['sensors'] = _init_sensors_data()
    config['rfid'] = _init_rfid_data()

    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w') as configfile:
        config.write(configfile)

    logging.info(f"Configuration file successfully created in: {config_path}")
