#!/usr/bin/env python
# coding=utf-8
# @Time    : 2021/8/23 11:22
# @Author  : 江斌
# @Software: PyCharm

import time
from TemplateProject.connections.zmq_push_pull import get_pusher, get_puller

puller = get_puller('tcp://*:6555')
idx = 1

while True:
    idx = idx + 1
    data = {"name": f"python{idx}"}
    msg = puller.receiver.recv()
    print(f"puller recv: {msg}")
