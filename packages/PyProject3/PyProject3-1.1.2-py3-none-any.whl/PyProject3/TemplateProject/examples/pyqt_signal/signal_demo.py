# -*- coding: utf-8 -*-

'''
    【简介】
     对话框关闭时返回值给主窗口例子
'''

import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class DateDialog(QDialog):
    Signal_OneParameter = pyqtSignal(str)  # 自定义一个带参的信号

    def __init__(self, parent=None):
        super(DateDialog, self).__init__(parent)
        self.setWindowTitle('子窗口：用来发射信号')

        # 在布局中添加部件
        layout = QVBoxLayout(self)

        self.label = QLabel(self)
        self.label.setText('前者发射内置信号\n后者发射自定义信号')

        self.datetime_inner = QDateTimeEdit(self)
        self.datetime_inner.setCalendarPopup(True)
        self.datetime_inner.setDateTime(QDateTime.currentDateTime())

        self.datetime_emit = QDateTimeEdit(self)
        self.datetime_emit.setCalendarPopup(True)
        self.datetime_emit.setDateTime(QDateTime.currentDateTime())

        layout.addWidget(self.label)
        layout.addWidget(self.datetime_inner)
        layout.addWidget(self.datetime_emit)

        # 使用两个button(ok和cancel)分别连接accept()和reject()槽函数
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.datetime_emit.dateTimeChanged.connect(self.emit_signal)

    def emit_signal(self):
        date_str = self.datetime_emit.dateTime().toString()
        self.Signal_OneParameter.emit(date_str)  # 通过内置信号发送自自定义的信号


class WinForm(QWidget):
    def __init__(self, parent=None):
        super(WinForm, self).__init__(parent)
        self.resize(400, 90)
        self.setWindowTitle('信号与槽传递参数的示例')

        self.open_btn = QPushButton('获取时间')
        self.lineEdit_inner = QLineEdit(self)
        self.lineEdit_emit = QLineEdit(self)
        self.open_btn.clicked.connect(self.openDialog)

        self.lineEdit_inner.setText('接收子窗口内置信号的时间')
        self.lineEdit_emit.setText('接收子窗口自定义信号的时间')

        grid = QGridLayout()
        grid.addWidget(self.lineEdit_inner)
        grid.addWidget(self.lineEdit_emit)

        grid.addWidget(self.open_btn)
        self.setLayout(grid)

    def openDialog(self):
        dialog = DateDialog(self)
        '''连接子窗口的内置信号与主窗口的槽函数'''
        dialog.datetime_inner.dateTimeChanged.connect(self.deal_inner_slot)
        '''连接子窗口的自定义信号与主窗口的槽函数'''
        dialog.Signal_OneParameter.connect(self.deal_emit_slot)
        dialog.show()

    def deal_inner_slot(self, date):  # 内置信号槽函数
        self.lineEdit_inner.setText(date.toString())

    def deal_emit_slot(self, dateStr):  # 自定义信号槽函数
        self.lineEdit_emit.setText(dateStr)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = WinForm()
    form.show()
    sys.exit(app.exec_())
