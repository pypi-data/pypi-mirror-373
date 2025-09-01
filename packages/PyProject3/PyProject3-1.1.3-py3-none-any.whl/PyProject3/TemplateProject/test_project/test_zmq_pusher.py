#!/usr/bin/env python
# coding=utf-8
# @Time    : 2021/8/23 11:22
# @Author  : 江斌
# @Software: PyCharm
"""
pusher与puller配合使用。
    pusher 推送数据。
    puller 拉取数据。
"""
import time
from TemplateProject.connections.zmq_push_pull import get_pusher, get_puller

pusher = get_pusher('tcp://127.0.0.1:6555')
idx = 1

while True:
    idx = idx + 1
    data = {"name": f"python{idx}"}
    pusher.sender.send_json(data)
    time.sleep(1)
