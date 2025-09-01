#!/usr/bin/env python
# coding=utf-8
# @Time    : 2021/8/23 11:47
# @Author  : 江斌
# @Software: PyCharm
import time
import threading


class SimpleThread(threading.Thread):
    def run(self):
        idx = 0
        while True:
            idx = idx + 1
            print(f'py-thread: {idx}')
            time.sleep(1)


def main():
    s = SimpleThread()
    # s.setDaemon(True)  # 设置成守护线程，主程序退出，自动结束。
    s.start()
    # s.join()  # 等待线程结束，阻塞程序继续执行
    print('zzz')


if __name__ == '__main__':
    main()
