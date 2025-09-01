import time
import paho.mqtt.client as mqtt


class MqttClient(object):
    def __init__(self, host, port, keep_alive=600):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(host, port, keep_alive)
        self.client.loop_start()

    def publish(self, topic, payload):
        """
        发布消息。
        :param topic:
        :param payload:
        :return:
        """
        self.client.publish(topic=topic, payload=payload)

    def subscribe(self, topic, qos=0):
        """
        订阅消息。
        :param topic:
        :param qos:
        :return:
        """
        self.client.subscribe(topic, qos)

    def on_connect(self, client, userdata, flags, rc):
        print(f"[on_connect] client: {client}; Connected with result code: {rc}")

    def on_message(self, client, userdata, msg):
        print(f'[on_message] client: {client}; topic:{msg.topic}; len:{len(msg.payload)} payload: {msg.payload}')


def test():
    def get_range(n):
        x = ''
        for i in range(n):
            x = f'{i}{x}'
        return x

    client = MqttClient('www.hiibotiot.com', 1883)
    client.subscribe('/test/topic1')

    while True:
        idx = 20
        client.publish('/test/topic1', payload=get_range(1000 * idx))
        time.sleep(1)


if __name__ == '__main__':
    test()
