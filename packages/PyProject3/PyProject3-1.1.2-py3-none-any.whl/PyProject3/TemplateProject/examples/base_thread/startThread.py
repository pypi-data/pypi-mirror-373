# coding=utf-8

import threading
import time

class SimpleThread(threading.Thread):
    def __init__(self):
        super(SimpleThread, self).__init__()

    def run(self):
        n = 0
        while True:
            n = n + 1
            print("hello ", n)
            time.sleep(1)
            print("world ", n)
            time.sleep(1)

    def start(self):
        super(SimpleThread, self).start()


st = SimpleThread()
st.start()
time.sleep(3)
