#!/usr/bin/env python
# coding=utf-8
# @Time    : 2020/9/22 11:15
# @Author  : 江斌
# @Software: PyCharm

from PyQt5 import QtWidgets, QtCore, QtMultimedia, QtMultimediaWidgets
import sys

app = QtWidgets.QApplication(sys.argv)
url = QtCore.QUrl.fromLocalFile(r"C:\Users\Admin\Music\music\云菲菲 - 那条街.mp3")
url = QtCore.QUrl.fromLocalFile(r"C:\Users\Admin\Videos\2020-02-18 20-22-13.mp4")
content = QtMultimedia.QMediaContent(url)
player = QtMultimedia.QMediaPlayer()

widget = QtMultimediaWidgets.QVideoWidget()
player.setVideoOutput(widget)
player.setMedia(content)
player.setVolume(10)
widget.showMaximized()
player.play()
sys.exit(app.exec())