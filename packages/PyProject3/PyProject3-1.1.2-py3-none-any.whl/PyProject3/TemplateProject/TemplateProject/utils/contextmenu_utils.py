#!/usr/bin/env python
# coding=utf-8
# @Time    : 2021/1/25 14:17
# @Author  : 江斌
# @Software: PyCharm
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMenu, QAction, QWidget, QApplication, QMessageBox
import os
import sys
from functools import partial


def open_dir(filepath):
    os.startfile(filepath)


class ContextMenu(object):
    def show_root_menu(self, pos, widget):
        menu = QMenu()
        action1 = QAction("打开项目根目录...", parent=menu)
        # action1 = QAction("打开项目根目录...", parent=menu)
        action1.triggered.connect(partial(open_dir, 'T:/'))
        actions = [
            action1,
            # action2
        ]
        menu.addActions(actions)
        if widget is not None:
            menu.exec_(widget.mapToGlobal(pos))
        else:
            menu.exec_(pos)

    @staticmethod
    def test_menu():
        app = QApplication(sys.argv)
        cm = ContextMenu()
        widget = QWidget()
        widget.setContextMenuPolicy(Qt.CustomContextMenu)
        widget.customContextMenuRequested.connect(partial(cm.show_root_menu, widget=widget))
        widget.show()
        sys.exit(app.exec_())


if __name__ == '__main__':
    ContextMenu.test_menu()
