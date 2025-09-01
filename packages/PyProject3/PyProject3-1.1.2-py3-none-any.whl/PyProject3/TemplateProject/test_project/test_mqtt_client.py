#!/usr/bin/env python
# coding=utf-8
# @Time    : 2021/8/23 11:01
# @Author  : 江斌
# @Software: PyCharm

import time
import json
import unittest
from TemplateProject import settings
from TemplateProject.connections.mqtt_client import MqttClient


class TestMain(unittest.TestCase):
    def test_mqtt(self):
        client = MqttClient('www.hiibotiot.com', 1883)  # tcp
        client.subscribe('/test/topic1')
        count = 10
        while count:
            count = count - 1
            data = {"name": f"python{count}"}
            client.publish('/test/topic1', payload=json.dumps(data))
            time.sleep(1)

    def testSpsToFbx(self):
        a = 0.00001
        b = 77
        c = True
        self.assertLess(a, 0.001, f'assert error: {a}>0.001')
        self.assertEqual(b, 77)
        self.assertTrue(c)
