#!/usr/bin/env python
# coding=utf-8
# @Time    : 2021/8/19 19:00
# @Author  : 江斌
# @Software: PyCharm
import time
from system_hotkey import SystemHotkey

hk = SystemHotkey()
hk.register(('control', 'alt', 'a'), callback=lambda x: print("Easy!"))

while True:
    time.sleep(1)
