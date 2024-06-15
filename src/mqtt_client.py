import paho.mqtt.client as mqtt


class MqttClient:
    def __init__(self, config) -> None:
        self.client = mqtt.Client()
        self.client.username_pw_set(config.username, config.password)
        self.client.connect(config.broker_url, config.broker_port)

    def publish_message(self, topic, message) -> None:
        self.client.publish(topic, message)

    def disconnect(self) -> None:
        self.client.disconnect()
