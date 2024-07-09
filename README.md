# PiAlarmAdapter

[![CI Pipeline](https://github.com/francescoscanferla/PiAlarmAdapter/actions/workflows/ci.yml/badge.svg)](https://github.com/francescoscanferla/PiAlarmAdapter/actions/workflows/ci.yml) [![Coverage Status](https://coveralls.io/repos/github/francescoscanferla/PiAlarmAdapter/badge.svg?branch=main)](https://coveralls.io/github/francescoscanferla/PiAlarmAdapter?branch=main)

Application to manage contact sensors and send messages with state change to an MQTT Broker.



## Environment variables

| Variable             |  Default  | Info                                                           |
|----------------------|:---------:|----------------------------------------------------------------|
| **LOG_LEVEL**        |   INFO    | Level of logger. Valori possibili: DEBUG, INFO, WARNING, ERROR |
| **MQTT_BROKER_URL**  | 127.0.0.1 | IP address of the MQTT broker                                  |
| **MQTT_BROKER_PORT** |   1883    | Port number of the MQTT Broker                                 |
| **MQTT_USERNAME**    |   admin   | Username that can post messages on queues                      |
| **MQTT_PASSWORD**    |   admin   | password of the user above                                               |

For sensor configuration, add environment variables in the format:
SENSOR_<NOME_SENSORE>=<PIN_NUMBER>

Example: **SENSOR_BEDROOM=4**