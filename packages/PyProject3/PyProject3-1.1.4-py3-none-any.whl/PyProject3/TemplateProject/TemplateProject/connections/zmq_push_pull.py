# coding=utf-8

import zmq
import time
import traceback

import logging

logger = logging.getLogger("motion_mocap_proxy")

if hasattr(zmq, 'SNDHWM'):
    zmq.HWM = zmq.SNDHWM

ZEROMQ_DEFAULT_HWM = 100000


class Pusher(object):
    def __init__(self, endpoint, options={}):
        ctx = zmq.Context()
        self.sender = ctx.socket(zmq.PUSH)
        self.sender.setsockopt(zmq.HWM, ZEROMQ_DEFAULT_HWM)
        self.sender.setsockopt(zmq.TCP_KEEPALIVE, 1)
        self.sender.setsockopt(zmq.TCP_KEEPALIVE_CNT, 10)
        self.sender.setsockopt(zmq.TCP_KEEPALIVE_IDLE, 1)
        self.sender.setsockopt(zmq.TCP_KEEPALIVE_INTVL, 1)
        for k, v in options.items():
            self.sender.setsockopt(k, v)
        self.sender.connect(endpoint)
        logger.info('connect push addr: %s', endpoint)
        time.sleep(0.2)

    def __del__(self):
        self.sender.setsockopt(zmq.LINGER, 0)
        self.sender.close()

    def send(self, msg):
        self.sender.send(msg)


class MultiPusher(object):
    def __init__(self, endpoints, options={}):
        self.pusher_list = [get_pusher(endpoint, options) for endpoint in endpoints]

    def send(self, msg):
        for pusher in self.pusher_list:
            pusher.send(msg)


class Puller(object):
    def __init__(self, endpoint):
        ctx = zmq.Context()
        self.receiver = ctx.socket(zmq.PULL)
        self.receiver.setsockopt(zmq.HWM, ZEROMQ_DEFAULT_HWM)
        self.receiver.bind(endpoint)
        logger.info('bind pull addr: %s', endpoint)
        time.sleep(0.2)

    def run(self):
        while True:
            msg = self.receiver.recv()
            self.work(msg)

    def work(self, msg):
        try:
            print(msg)
        except:
            print(traceback.format_exc())


# pusher_endpoint = 'tcp://127.0.0.1:11980'
# puller_endpoint = 'tcp://*:11980'
def get_pusher(endpoint, options={}):
    pusher = Pusher(endpoint, options)
    return pusher


def get_multi_pusher(endpoints, options={}):
    return MultiPusher(endpoints, options)


def get_puller(endpoint):
    puller = Puller(endpoint)
    return puller
