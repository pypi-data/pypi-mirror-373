#!/usr/bin/env python
# coding=utf-8
# @Time    : 2021/3/9 15:03
# @Author  : 江斌
# @Software: PyCharm

import sys
import json
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QBrush, QColor
from PyQt5.QtCore import Qt
from PyQt5 import QtCore


class LineEditDelegate(QItemDelegate):
    def createEditor(self, parent: QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex):
        editor = QLineEdit(parent=parent)
        editor.setFixedHeight(120)
        # editor.setValidator(QIntValidator(parent))
        return editor

    def setEditorData(self, editor: QWidget, index: QtCore.QModelIndex):
        text = index.model().data(index)
        editor.setText(text)
        print('setEditorData')

    def setModelData(self, editor: QWidget, model: QtCore.QAbstractItemModel, index: QtCore.QModelIndex):
        text = editor.text()
        model.setData(index, text, Qt.EditRole)
        print('setModelData')

    def updateEditorGeometry(self, editor: QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex):
        editor.setGeometry(option.rect)


class MyQTreeWidget(QTreeWidget):
    data_changed_signal = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        super(MyQTreeWidget, self).__init__(parent)
        self.setColumnCount(2)
        self.setHeaderLabels(['Key', 'Value'])
        self.setColumnWidth(0, 200)
        # self.tree.clicked.connect(self.onTreeClicked)

    def dataChanged(self, topLeft, bottomRight, roles):
        try:
            item = self.currentItem()
            if item is not None:
                print("node changed, new_key=%s ,new_value=%s" % (item.text(0), item.text(1)))
                data = self.data()
                self.data_changed_signal.emit(data)
        except:
            pass

    def data(self):
        parent = self.topLevelItem(0)
        while True:
            tmp = parent.parent()
            if tmp is None:
                break
            else:
                parent = tmp
        data2 = {}
        self._get_data(parent=parent, data=data2)
        return data2['root']

    def _get_data(self, parent, data):
        key = parent.text(0)
        data[key] = {}
        if parent.childCount() > 0:
            for idx in range(parent.childCount()):
                item = parent.child(idx)
                self._get_data(item, data[key])
        else:
            value = parent.text(1)
            value = eval(value)
            data[key] = value

    def load_json(self, d):
        if isinstance(d, dict):
            self.clear()
            self.add_children(d)
            self.expandAll()

    def load_json_file(self, json_file):
        with open(json_file, 'r') as f:
            d = json.load(f)
            self.load_json(d)

    def add_children(self, child_dict, root=None):
        if root is None:
            root = QTreeWidgetItem(self)  # 设置根节点
            root.setText(0, 'root')
            root.setIcon(0, QIcon("./res/camera.png"))

            # 设置节点的背景颜色
            grey = QBrush(QColor(125, 125, 225))  # Qt.red  Qt.green
            root.setBackground(0, grey)
            root.setBackground(1, grey)
        for key, value in child_dict.items():
            if isinstance(value, dict):
                item = QTreeWidgetItem(root)  # 设置根节点
                # self.setItemDelegate(LineEditDelegate())  # 设置item委托
                item.setIcon(0, QIcon("./res/editor-bracket-big.png"))
                item.setText(0, str(key))
                self.add_children(value, root=item)
            else:
                if isinstance(value, str):
                    val = f'"{value}"'
                else:
                    val = f'{value}'
                # val = f'{value}'
                item = QTreeWidgetItem(root)  # 创建子节点
                item.setText(0, key)  # 设置第一列的值
                item.setText(1, val)  # 设置第二列的值
                # item.setIcon(0, QIcon("./res/radar.png"))
                if key == 'R':
                    item.setBackground(0, QColor(255, 225, 225))
                    item.setBackground(1, QColor(255, 225, 225))
                if key == 'T':
                    item.setBackground(0, QColor(225, 255, 225))
                    item.setBackground(1, QColor(225, 255, 225))
                # item.setCheckState(0, Qt.Checked)  # 设置第一列选中状态
                item.setFlags(Qt.ItemIsEditable | Qt.ItemIsEnabled)

        self.addTopLevelItem(root)

    def onTreeClicked(self):
        item = self.currentItem()
        print("key=%s ,value=%s" % (item.text(0), item.text(1)))

    def itemChanged(self, item, index):
        print("key=%s ,value=%s" % (item.text(0), item.text(1)))


def test():
    app = QApplication(sys.argv)
    tree = MyQTreeWidget()

    d = {"child-1": "Python",
         "child-2": "Java",
         "child-3": "C++",
         "child-4": "C",
         "child-5": {
             "bone1": [111, 12, 30],
             "bone2": 'abc'
         }
         }
    tree.load_json(d)
    tree.show()
    sys.exit(app.exec_())


def test_load_file():
    app = QApplication(sys.argv)
    tree = MyQTreeWidget()
    tree.load_json_file(r"D:/data/Retarget/Character/xiaowen_new.json")
    tree.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    test_load_file()
