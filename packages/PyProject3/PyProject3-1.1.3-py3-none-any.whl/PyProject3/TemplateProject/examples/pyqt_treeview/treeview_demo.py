#!/usr/bin/env python
# coding=utf-8
# @Time    : 2021/8/26 16:09
# @Author  : 江斌
# @Software: PyCharm

# !/usr/bin/env python
# -*- coding:utf-8 -*-

from PyQt5 import QtGui, QtWidgets, QtCore

import sys, os


class TreeView(QtWidgets.QTreeView):
    def __init__(self, parent=None):
        super(TreeView, self).__init__(parent)

        self.__model = QtWidgets.QFileSystemModel(self)
        self.__model.setRootPath(QtCore.QDir.rootPath())
        self.setModel(self.__model)

        self.cur_item = None
        self.clicked.connect(self.on_select_changed)
        self.doubleClicked.connect(self.on_double_clicked)
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.set_menu)  ####右键菜单
        self.setAcceptDrops(True)

    # 双击信号 获得当前选中的节点的路径
    def on_select_changed(self):
        index = self.currentIndex()
        model = index.model()  # 请注意这里可以获得model的对象
        self.cur_item = model.filePath(index)

    def on_double_clicked(self):
        # index = self.currentIndex()
        # model = index.model()  # 请注意这里可以获得model的对象
        # self.cur_item = model.filePath(index)
        os.startfile(self.cur_item)

    def set_menu(self, pos):
        menu = QtWidgets.QMenu(self)
        open_action = menu.addAction("打开文件目录...")
        copy_action = menu.addAction("复制路径...")
        open_action.triggered.connect(self.open_current_dir)
        copy_action.triggered.connect(self.copy_path)
        menu.exec_(self.mapToGlobal(pos))

    def open_current_dir(self):
        d = self.cur_item if os.path.isdir(self.cur_item) else os.path.dirname(self.cur_item)
        os.startfile(d)

    def copy_path(self):
        clipboard = QtWidgets.QApplication.clipboard()
        print(type(self.cur_item))
        clipboard.setText(self.cur_item)

    # 设置TreeView的跟文件夹
    def setPath(self, path):
        self.setRootIndex(self.__model.index(path))

    # 获得当前选中的节点的路径
    def getCurPath(self):
        return self.cur_item

    def dragEnterEvent(self, e):
        mime_data = e.mimeData()
        print(mime_data)
        if mime_data.hasUrls:
            url = mime_data.urls()[0].toLocalFile()
            d = os.path.dirname(url) if os.path.isfile(url) else url
            if os.path.isdir(d):
                self.setPath(d)
            e.accept()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    asset = TreeView()
    asset.setPath(r"C:\users")
    asset.setPath(r"D:\data\Retarget")
    asset.show()

    sys.exit(app.exec_())
