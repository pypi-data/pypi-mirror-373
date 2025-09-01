#!/usr/bin/env python
# coding=utf-8
# @Time    : 2021/3/10 11:32
# @Author  : 江斌
# @Software: PyCharm
from .zmq_push_pull import get_puller, get_pusher
from .zmq_pub_sub import get_subber
from .zmq_message_compress import MessageCompress, LZ4_HEAD, START
import time
import msgpack
import threading
import logging
import lz4.block as lz4
from PyQt5.Qt import QObject, pyqtSignal

logger = logging.getLogger()


class ZmqMessage(object):
    def __init__(self, msg):
        self.compress_message = msg
        self.compress_ratio = None
        self.compress_method = self.get_compress_method()
        self.uncompress_message = self.decompress()

    def get_compress_method(self):
        if len(self.compress_message) > len(LZ4_HEAD) and self.compress_message[0:len(LZ4_HEAD)] == LZ4_HEAD:
            return 'lz4'
        else:
            return 'msgpack'

    def decompress(self):
        msg = None
        if self.compress_method == 'lz4':
            # msg = MessageCompress.decompress_by_lz4(self.compress_message)
            data_msgpack = lz4.decompress(self.compress_message[START:])
            msg = msgpack.unpackb(data_msgpack)
            self.compress_ratio = len(self.compress_message) / len(data_msgpack)
        if self.compress_method == 'msgpack':
            msg = msgpack.unpackb(self.compress_message)
        return msg

    def __str__(self):
        time_stamp = self.uncompress_message.get('data', {}).get('XCTimeStamp', None)
        return f'ZmqMessage({"timestamp="+time_stamp+"," if time_stamp else ""}' \
               f'len={len(self.compress_message)}, ' \
               f' method="{self.compress_method}", ' \
               f'message={self.compress_message[0:min(10, len(self.compress_message))]})'

    def __repr__(self):
        return self.__str__()

    def summary(self):
        info = ''
        try:
            if 'data_type' in self.uncompress_message:
                info += f'data_type: {self.uncompress_message.get("data_type", "unknown")}\n'
            info += f'压缩方式：{self.compress_method}\n'
            if self.compress_method == 'lz4':
                info += f'压缩比：{self.compress_ratio:1.3f} : 1\n'
                header = MessageCompress.unpack_header(self.compress_message)
                info += f'时间戳：{header["timestamp"]}\n'
            info += f'压缩数据长度：{len(self.compress_message)}\n'
            if 'skeleton_frame' in self.uncompress_message['data']:
                skeleton_frame_num = len(self.uncompress_message['data']['skeleton_frame'].keys())
                info += f'骨骼数：{skeleton_frame_num}'
        except Exception as e:
            print(e)
        return info


class ZmqReceiver(QObject):
    msg_signal = pyqtSignal(object)

    def __init__(self, endpoint):
        super(ZmqReceiver, self).__init__()
        self.endpoint = endpoint
        self._stop = False
        self.subber = get_subber(self.endpoint, '')
        self.recv_thread = None

    def start(self):
        self.recv_thread = threading.Thread(target=self._recv, daemon=True)
        self.recv_thread.start()

    def stop(self):
        self._stop = True  # 暂停接送线程

    def _recv(self):
        while True:
            if self._stop:
                break
            msg = self.subber.receiver.recv()
            if msg is None:
                time.sleep(0.001)
                continue
            else:
                data = ZmqMessage(msg=msg)
                self.msg_signal.emit(data)


class ZmqPuller(QObject):
    msg_signal = pyqtSignal(object)

    def __init__(self, endpoint):
        super(ZmqPuller, self).__init__()
        self.puller = get_puller(endpoint)
        self._stop = False

    def start(self):
        self.recv_thread = threading.Thread(target=self._recv, daemon=True)
        self.recv_thread.start()

    def stop(self):
        self._stop = True

    def _recv(self):
        while True:
            if self._stop:
                self.puller.receiver.close(linger=0)
                break
            msg = self.puller.receiver.recv()
            if msg is None:
                time.sleep(0.001)
                continue
            else:
                data = ZmqMessage(msg=msg)
                # print(data)
                self.msg_signal.emit(data)


def test_puller():
    puller = ZmqPuller(endpoint='tcp://127.0.0.1:5556')
    puller.start()
    puller.recv_thread.join()


if __name__ == '__main__':
    test_puller()
