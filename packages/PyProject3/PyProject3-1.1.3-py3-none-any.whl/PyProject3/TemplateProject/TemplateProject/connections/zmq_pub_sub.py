import zmq
import time
import json
import traceback

import logging
logger = logging.getLogger("motion_mocap_proxy")


if hasattr(zmq, 'SNDHWM'):
    zmq.HWM = zmq.SNDHWM

ZEROMQ_DEFAULT_HWM = 100000


class Pubber(object):
    def __init__(self, endpoint):
        ctx = zmq.Context()
        self.sender = ctx.socket(zmq.PUB)
        self.sender.setsockopt(zmq.HWM, ZEROMQ_DEFAULT_HWM)
        self.sender.bind(endpoint)
        logger.info('bind pub addr: %s', endpoint)
        time.sleep(0.2)

    def send_with_topic(self, topic, msg):
        msg = json.dumps(msg)
        msg = "%s %s"%(topic, msg)
        self.sender.send_string(msg)
        time.sleep(0.1)

    def send(self, msg):
        self.sender.send_json(msg)


class Subber(object):
    def __init__(self, endpoint, topic):
        ctx = zmq.Context()
        self.receiver = ctx.socket(zmq.SUB)
        self.receiver.setsockopt(zmq.HWM, ZEROMQ_DEFAULT_HWM)
        self.receiver.setsockopt(zmq.TCP_KEEPALIVE, 1)
        self.receiver.setsockopt(zmq.TCP_KEEPALIVE_CNT, 10)
        self.receiver.setsockopt(zmq.TCP_KEEPALIVE_IDLE, 1)
        self.receiver.setsockopt(zmq.TCP_KEEPALIVE_INTVL, 1)
        try:
            self.receiver.subscribe(topic)
        except:
            self.receiver.setsockopt(zmq.SUBSCRIBE, topic)
        self.receiver.connect(endpoint)
        self.stop_flag = False
        logger.info('connect sub addr: %s', endpoint)
        time.sleep(0.2)

    def run(self, work_func, fps=None):
        last_msg = None
        start_ts = time.time()
        while not self.stop_flag:
            msg = self.receiver.recv_json()
            if fps:
                ts_interval = 1 / fps
                if time.time() - start_ts < ts_interval:
                    continue

            start_ts = time.time()  # 计时包含work_func的执行时间
            work_func(msg, last_msg)
            last_msg = msg

    def stop(self):
        self.stop_flag = True

    def test_run(self):
        while True:
            msg = self.receiver.recv_json()
            self.test_work(msg)

    def test_work(self, msg):
        try:
            print(type(msg), msg)
        except:
            print(traceback.format_exc())


# pubber_endpoint = 'tcp://*:11990'
# subber_endpoint = 'tcp://127.0.0.1:11990'
def get_subber(endpoint, topic):
    subber = Subber(endpoint, topic)
    return subber

def get_pubber(endpoint):
    pubber = Pubber(endpoint)
    return pubber
