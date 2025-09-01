#!/usr/bin/env python
# coding=utf-8
# @Time    : 2020/9/18 11:04
# @Author  : 江斌
# @Software: PyCharm
import sys
from PyQt5 import QtGui

from PyQt5.QtWidgets import QSystemTrayIcon, QApplication


class MyTray(QSystemTrayIcon):
    def __init__(self):
        super().__init__()
        try:
            self.setIcon(QtGui.QIcon(r"C:\Users\Admin\Pictures\p.png"))
            self.activated.connect(self.iconClicked)
        except Exception as e:
            print(e)

    def bind(self, window):
        self.parent_window = window

    def test(self):
        try:
            self.parent_window.show()
        except Exception as e:
            print(e)

    def iconClicked(self, reason):
        # 鼠标点击icon传递的信号会带有一个整形的值，1是表示单击右键，2是双击，3是单击左键，4是用鼠标中键点击"
        print('click')
        if reason == 2:  # 2是双击
            self.test()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MyTray()
    w.show()
    sys.exit(app.exec_())

