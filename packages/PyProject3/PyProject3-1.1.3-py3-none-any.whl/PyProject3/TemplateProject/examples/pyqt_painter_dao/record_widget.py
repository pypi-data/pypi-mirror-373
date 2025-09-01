#!/usr/bin/env python
# coding=utf-8
# @Time    : 2021/8/29 17:46
# @Author  : 江斌
# @Software: PyCharm

import os
import sys
import time
import json
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from pyqt5extras import StyledButton, SegmentedButtonGroup


class RecordWidget(QWidget):
    def __init__(self, parent=None):
        super(RecordWidget, self).__init__(parent=parent)
        self.init_ui()
        self.setMaximumHeight(50)

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def init_ui(self):
        # self.setStyleSheet("background:black;")
        layout = QHBoxLayout()
        layout.setSpacing(0)
        btn1 = StyledButton('▶')
        btn1.setMinimumSize(40, 40)
        btn1.setStyleDict({"radius-corners": (True, False, True, False),
                           'border-width': 1,
                           "border-radius": 40,
                           "border-color": (0, 0, 0),
                           "background-color": (241, 241, 241),
                           "font-size": 50,
                           "color": (50, 170, 80)
                           })
        btn1.setStyleDict({
            "background-color": (200, 0, 0),
            "color": (255, 255, 255)
        }, "hover")
        btn1.setStyleDict({
            "background-color": (255, 0, 0),
            "color": (255, 255, 255)
        }, "press")
        edit = QLabel('请输入...')
        edit.setStyleSheet("border:1px solid black;background: rgb(240, 240, 240);")
        btn2 = StyledButton(icon="homeicon.png")
        btn2.setIconSize(30, 30)
        btn2.setMinimumSize(40, 40)
        btn2.setStyleDict({"radius-corners": (False, True, False, True),
                           'border-radius': 40,
                           "border-color": (0, 0, 0),
                           "background-color": (241, 241, 241),
                           'border-width': 1})

        btn2.setStyleDict({
            "background-color": (200, 0, 0),
            "color": (255, 255, 255)
        }, "hover")
        btn2.setStyleDict({
            "background-color": (255, 0, 0),
            "color": (255, 255, 255)
        }, "press")
        btn1.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        edit.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        btn2.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        layout.addWidget(btn1)
        layout.addWidget(edit)
        layout.addWidget(btn2)
        self.setLayout(layout)

    def paintEvent(self, a0: QtGui.QPaintEvent):
        pass


class ExampleWidget(QLabel):
    def __init__(self, text):
        super(ExampleWidget, self).__init__(text)
        self.setAcceptDrops(True)
        self.setGeometry(300, 300, 300, 150)
        self.setStyleSheet(" font-size:20px; color:gray;")

    def init_ui(self):
        pass

    def dragEnterEvent(self, e):
        self.setStyleSheet("background-color:#aaa;")
        mime_data = e.mimeData()
        if mime_data.hasUrls:
            for url in mime_data.urls():
                print('drag enter: ', url.toLocalFile())
            e.accept()
            return
        if mime_data.hasFormat("text/plain"):
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        mime_data = e.mimeData()
        print(mime_data.urls())
        if mime_data.hasUrls():
            url = mime_data.urls()[0]
            self.setText(url.toLocalFile())  # url.toString()


def main():
    app = QApplication(sys.argv)
    ex = RecordWidget()
    ex.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
