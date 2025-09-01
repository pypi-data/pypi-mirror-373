#!/usr/bin/env python
# coding=utf-8
# @Time    : 2021/1/23 17:34
# @Author  : 江斌
# @Software: PyCharm
import time
import math
import threading
from ctypes import windll  # new

timeBeginPeriod = windll.winmm.timeBeginPeriod  # new
timeEndPeriod = windll.winmm.timeEndPeriod  # new

ret = timeBeginPeriod(1)  # new


class Clock(object):
    RESOLUTION_ms = 2  # 电脑的tick精度
    HALF_RESOLUTION_ms = 1

    def __init__(self, fps=120):
        # self.update_resolution()
        self.start = time.perf_counter()
        self._fps = None
        self.frame_length = None
        self.sleep_block_num = 2
        self.fps = fps

    @property
    def fps(self):
        return self._fps

    @fps.setter
    def fps(self, new_value):
        self._fps = new_value
        self.frame_length = 1 / self._fps
        if Clock.RESOLUTION_ms >= self.frame_length:
            self.sleep_block_num = 2
        else:
            self.sleep_block_num = 1

    @staticmethod
    def update_resolution():
        """ 更新精度。不同windows环境下，time.sleep(0.001)实际睡眠的时间长短不一。2ms-15ms都有。 """
        res_list = []
        N = 10
        for i in range(N):
            t1 = time.perf_counter()
            time.sleep(0.001)
            t2 = time.perf_counter()
            res_list.append(t2 - t1)
        mean_res = sum(res_list) / len(res_list)
        Clock.RESOLUTION_ms = min(8.0, math.ceil(mean_res * 1000))
        Clock.HALF_RESOLUTION_ms = min(4.0, math.ceil(mean_res / 2 * 1000))

    @property
    def tick(self):
        """ 当前帧数。 """
        return int((time.perf_counter() - self.start) / self.frame_length)

    # def sleep(self):
    #     """ 等待一帧的时间。 """
    #     r = self.tick + 1
    #     while self.tick < r:
    #         time.sleep(1 / 1000)

    def sleep_ms(self, n):
        """
        高精度延时ms。原理：使用两段sleep来提高精度，第一段使用time.sleep粗略延时，第二段空循环精确延时。
        :param n: 毫秒数。可以使用小数，以达到微秒级别的延时。
        :return:
        """
        st = time.perf_counter()
        # 第一段粗略延时。
        if n > self.RESOLUTION_ms:
            dt_s = (n - self.RESOLUTION_ms) / 1000
            # print(f'sleep {dt_s}s')
            time.sleep(dt_s)

        # 第二段精确延时。
        dt_ms = (time.perf_counter() - st) * 1000
        while dt_ms < n:
            dt_ms = (time.perf_counter() - st) * 1000
            pass
        return dt_ms


Clock.update_resolution()


class Timer(object):
    def __init__(self, fps=120, callback=None):
        self.callback = callback
        self.thread = None
        self.stop_flag = False
        self.clock = None
        self._fps = fps
        self.fps = fps

    @property
    def fps(self):
        return self._fps

    @fps.setter
    def fps(self, new_value):
        self._fps = new_value
        self.clock = Clock(fps=self._fps)
        self.stop_flag = True
        if self.thread is not None:
            while self.thread.is_alive():
                time.sleep(0.001)
        print('stop thread')
        self.stop_flag = False
        self.thread = threading.Thread(target=self.loop)
        self.thread.start()

    def loop(self):
        while not self.stop_flag:
            if self.callback is not None:
                self.callback()
                # print(f'{1/self.fps}')
                self.clock.sleep_ms(1000 / self.fps)

    def stop(self):
        if self.thread is not None:
            self.stop_flag = True


def test_clock():
    clock = Clock()
    print(clock.RESOLUTION_ms)
    print(clock.HALF_RESOLUTION_ms)
    print(clock.sleep_ms(10))


def test_timer():
    def callback():
        print('hello')

    t = Timer(callback=callback, fps=1)
    time.sleep(10)
    t.fps = 5  # 重置


if __name__ == '__main__':
    # test_clock()
    test_timer()
