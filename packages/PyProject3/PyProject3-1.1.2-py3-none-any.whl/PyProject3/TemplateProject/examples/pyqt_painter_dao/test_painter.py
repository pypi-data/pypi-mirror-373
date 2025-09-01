import os
import sys
import math
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import (QMainWindow, QWidget, QSlider, QApplication,
                             QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QMenu,
                             QDialog, QFormLayout, QTextEdit, QDialogButtonBox)
from PyQt5.QtCore import QObject, Qt, pyqtSignal, QPoint, QPointF
from PyQt5.QtGui import QPainter, QFont, QColor, QPen, QCursor, QImage
import pathlib
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QColor, QPainter, QPen, QBrush


class FileDetails:
    def __init__(self, path, content):
        self.path = path
        self.content = content
        self.size = len(self.content)

        self._path = pathlib.Path(self.path)

        self.name = self._path.name
        self.pureName = self._path.stem
        self.extension = self._path.suffix

    def __repr__(self):
        return f"<pyqt5Custom.FileDetails({self.name})>"


def get_radius(max_num=10):
    n = 0
    while True:
        for i in range(10, 30):
            n = n + 1
            yield i
        for i in range(30, 10, -1):
            n = n + 1
            yield i


class DragDropFile(QWidget):
    fileDropped = pyqtSignal(FileDetails)

    def __init__(self):
        super().__init__()

        self.setAcceptDrops(True)

        self.setMinimumSize(120, 65)

        self.borderColor = QColor(190, 190, 190)
        self.hoverBackground = QColor(245, 245, 250)
        self.borderRadius = 26
        self.borderWidth = 6

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.layout)

        self.title_lbl = QLabel("Drop your file here!")
        self.title_btn = QPushButton("Drophere!")
        self.title_btn.clicked.connect(self.test_btn)
        self.filename_lbl = QLabel("")

        self.layout.addWidget(self.title_lbl, alignment=Qt.AlignHCenter)
        self.layout.addSpacing(7)
        self.layout.addWidget(self.filename_lbl, alignment=Qt.AlignHCenter)
        self.layout.addWidget(self.title_btn, alignment=Qt.AlignHCenter)
        self.title_btn.clicked.connect(self.test_btn)
        self.title_lbl.setStyleSheet("font-size:19px;")
        self.filename_lbl.setStyleSheet("font-size:14px; color: #666666;")

        self.dragEnter = False

        self.file = None
        self.rg = get_radius()

    def test_btn(self):
        print('zzzzzz')

    def setTitle(self, title):
        self.title_lbl.setText(title)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            self.dragEnter = True
            event.accept()
            self.repaint()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.dragEnter = False
        self.repaint()

    def dropEvent(self, event):
        mime = event.mimeData()
        file = FileDetails(mime.urls()[0].toLocalFile(), mime.text())

        self.filename_lbl.setText(file.name)

        self.fileDropped.emit(file)
        btn = QPushButton(file.name)
        self.layout.addWidget(btn)
        # print(self.title_btn)
        self.dragEnter = False
        self.repaint()

    def paintEvent(self, event):
        pt = QPainter()
        pt.begin(self)
        pt.setRenderHint(QPainter.Antialiasing, on=True)
        path = QtGui.QPainterPath()
        # 创建一个QPainterPath对象后就会以坐标原点为当前点进行绘制，
        # 可以使用moveTo()
        # 函数改变当前点，移动当前点到点(50，250)
        self.r = next(self.rg)
        path.addEllipse(QPointF(130.0, 130.0), self.r, self.r)
        path.addEllipse(QPointF(100.0, 130.0), self.r, self.r)
        path.setFillRule(Qt.FillRule.WindingFill)
        # 绘制path

        pt.setPen(Qt.darkBlue)
        # pt.setClipPath(path)
        pt.setBrush(Qt.darkBlue)
        pt.drawPath(path)

        # pt.drawRect(0, 0 , 130, 130)
        # 平移坐标系统后再次绘制路径
        path.translate(200, 0)
        # pt.drawPath(path)
        pt.setPen(Qt.red)
        pt.end()
        # super(DragDropFile, self).paintEvent(e)

    def paintEvent1(self, event):
        pt = QPainter()
        pt.begin(self)
        pt.setRenderHint(QPainter.Antialiasing, on=True)
        path = QtGui.QPainterPath()
        # 创建一个QPainterPath对象后就会以坐标原点为当前点进行绘制，
        # 可以使用moveTo()
        # 函数改变当前点，移动当前点到点(50，250)
        path.moveTo(50, 50)
        # 从当前点即(50，250)绘制一条直线到点(50，230).完成后当前点更改为(50，230)
        path.lineTo(150, 50)
        # 从当前点和点(120，60)之间绘制一条三次贝塞尔曲线
        p1 = QPointF(150, 50)
        p2 = QPointF(250, 100)
        p3 = QPointF(350, 50)
        path.cubicTo(p1, p2, p3)

        path.lineTo(130, 130)
        # 向路径中添加一个椭圆
        path.addEllipse(QPointF(130.0, 130.0), 30, 30)
        # 绘制path
        pt.drawPath(path)

        # 平移坐标系统后再次绘制路径
        path.translate(200, 0)
        pt.setPen(Qt.darkBlue)
        pt.drawPath(path)
        pt.setPen(Qt.red)
        pt.drawEllipse(p1, 10, 10)
        pt.drawEllipse(p2, 10, 10)
        pt.drawEllipse(p3, 10, 10)
        pt.end()
        # super(DragDropFile, self).paintEvent(e)

    def paintEvent2(self, event):
        pt = QPainter()
        pt.begin(self)
        pt.setRenderHint(QPainter.Antialiasing, on=True)

        pen = QPen(self.borderColor, self.borderWidth, Qt.DotLine, Qt.RoundCap)
        pt.setPen(pen)

        if self.dragEnter:
            brush = QBrush(self.hoverBackground)
            pt.setBrush(brush)

        pt.drawRoundedRect(self.borderWidth, self.borderWidth, self.width() - self.borderWidth * 2,
                           self.height() - self.borderWidth * 2, self.borderRadius, self.borderRadius)

        pt.end()
        # super(DragDropFile, self).paintEvent(e)


app = QApplication(sys.argv)
ex = DragDropFile()
ex.show()
sys.exit(app.exec_())
