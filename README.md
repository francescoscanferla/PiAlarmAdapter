# PiAlarmAdapter

[![CI Pipeline](https://github.com/francescoscanferla/PiAlarmAdapter/actions/workflows/ci.yml/badge.svg)](https://github.com/francescoscanferla/PiAlarmAdapter/actions/workflows/ci.yml)
[![Coverage Status](https://coveralls.io/repos/github/francescoscanferla/PiAlarmAdapter/badge.svg?branch=main)](https://coveralls.io/github/francescoscanferla/PiAlarmAdapter?branch=main)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/b7e2b28d810c4ff8873175f5bc5db68d)](https://app.codacy.com/gh/francescoscanferla/PiAlarmAdapter/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)

![GitHub release](https://img.shields.io/github/v/release/francescoscanferla/PiAlarmAdapter.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Application to manage contact sensors and send messages with state change to an MQTT Broker.

## Install

### Prerequisite

It is necessary to have the library installed on the raspberry **gpiod**

### From PIP

You can use pip directly through the command:
> pip install pi_alarm_adapter

## Settings

### Environment variables

| Variable                 | Default | Info                                                                                          |
|--------------------------|:-------:|-----------------------------------------------------------------------------------------------|
| **LOG_LEVEL**            |  INFO   | Optional. Possible values: DEBUG, INFO, WARNING, ERROR. If not specified, the default is INFO |
| **GPIO_MOCK**            |  false  | If set to true enables GPIO virtualisation                                                    |
| **MOCK_INTERVAL**        |   10    | In debug mode it is the time between state changes                                            |

When running the application for the first time, you are prompted for the configurations that
will later be saved in the .PiAlarmAdapter folder inside the user's home folder

## ToDo List

- [X] move configuration from environment variables to a yaml file
- [X] Add periodic check of sensors
- Add support for NFC readers -> WIP