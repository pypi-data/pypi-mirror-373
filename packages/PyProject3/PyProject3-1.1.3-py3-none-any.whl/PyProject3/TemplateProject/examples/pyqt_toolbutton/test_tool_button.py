#!/usr/bin/env python
# coding=utf-8
# @Time    : 2020/10/19 19:20
# @Author  : 江斌
# @Software: PyCharm

from PyQt5.Qt import *
import sys


def get_ico(style):
    """

    :param style: QStyle.SP_arrow
    :return:
    """
    return QApplication.style().standardIcon(style)


def test_tool_button():
    app = QApplication(sys.argv)
    menu = QMenu()  # 创建菜单
    sub_menu = QMenu(menu)  # 创建子菜单
    sub_menu.setTitle("子菜单")
    sub_menu.setIcon(get_ico(QStyle.SP_TitleBarMaxButton))
    menu.addMenu(sub_menu)
    action = QAction(get_ico(QStyle.SP_ArrowForward), "行为", menu)
    menu.addAction(action)
    action.triggered.connect(lambda: print("点击了 action"))

    w = QWidget()
    layout = QVBoxLayout()
    w.setLayout(layout)
    w.setWindowTitle("QToolButton")
    w.resize(300, 300)

    tb = QToolButton()
    tb.setText('操作')
    tb.setIcon(get_ico(QStyle.SP_FileDialogListView))
    tb.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
    # tb.setArrowType(Qt.DownArrow)
    tb.setFixedWidth(80)
    tb.setFixedHeight(30)
    tb.setIconSize(QSize(30, 30))
    tb.setAutoRaise(True)
    tb.setMenu(menu)  # 添加菜单 到 QToolBool
    tb.setPopupMode(QToolButton.InstantPopup)  # 设置菜单模式
    # print(tb.arrowType())

    layout.addWidget(tb)
    # label = QLabel("Introduction")
    # label.setFixedHeight(20)
    # label.setPixmap(get_ico(QStyle.SP_MessageBoxWarning).pixmap(QSize(100, 100)))
    # label2 = QLabel("Introduction2")
    #
    # layout.addWidget(label)
    # layout.addWidget(label2)

    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    test_tool_button()
