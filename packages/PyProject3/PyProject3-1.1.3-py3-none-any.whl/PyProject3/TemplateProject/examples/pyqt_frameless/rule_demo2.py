# -*- coding: utf-8 -*-

"""
尺子。
"""
import sys
from PyQt5.QtWidgets import (QWidget, QSlider, QApplication,
                             QHBoxLayout, QVBoxLayout, QPushButton)
from PyQt5.QtCore import QObject, Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QPainter, QFont, QColor, QPen, QCursor
import winreg
import wmi


def get_device():
    PATH = "SYSTEM\\ControlSet001\\Enum\\"
    oWmi = wmi.WMI()
    # 获取屏幕信息
    monitors = oWmi.Win32_DesktopMonitor()
    m = monitors[0]
    subPath = m.PNPDeviceID
    infoPath = PATH + subPath + "\\Device Parameters"
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, infoPath)
    # 屏幕信息按照一定的规则保存（EDID）
    value = winreg.QueryValueEx(key, "EDID")[0]
    winreg.CloseKey(key)
    width, height = value[21], value[22]
    widthResolution = value[56] + (value[58] >> 4) * 256
    heightResolution = value[59] + (value[61] >> 4) * 256
    widthDensity = widthResolution / (width / 2.54)
    heightDensity = heightResolution / (height / 2.54)

    class info(object):
        width_cm = width
        height_cm = height
        width_resolution = widthResolution
        height_resolution = heightResolution
        width_ppi = widthDensity
        height_ppi = heightDensity

    return info


SCREEN_INFO = get_device()  # 屏幕信息


class RulerWidget(QWidget):
    def __init__(self):
        super(RulerWidget, self).__init__()
        self.initUI()

    def initUI(self):
        self.setMinimumSize(1, 60)

    def paintEvent(self, e):
        qpainter = QPainter()
        qpainter.begin(self)
        self.drawWidget(qpainter)
        qpainter.end()

    def drawWidget(self, qpainter):
        font = QFont('Serif', 7, QFont.Light)
        qpainter.setFont(font)

        size = self.size()
        w = size.width()
        h = size.height()
        print((w, h))
        pen = QPen(QColor(20, 20, 20), 1,
                   Qt.SolidLine)

        qpainter.setPen(pen)
        qpainter.setBrush(QColor(255, 175, 175, 100))
        qpainter.drawRect(0, 0, w - 1, h - 1)

        # 绘制厘米标尺
        num_mm = 0
        ppcm = SCREEN_INFO.width_resolution / SCREEN_INFO.width_cm
        pen = QPen(QColor(200, 0, 0), 1,
                   Qt.SolidLine)
        qpainter.setPen(pen)
        for i in range(0, SCREEN_INFO.width_cm * 10):
            int_i = round(i * ppcm / 10)
            qpainter.drawLine(int_i, 0, int_i, 5 if i % 5 != 0 else 10)
            num_mm = num_mm + 1

        num_cm = 0
        pen = QPen(QColor(200, 0, 0), 2,
                   Qt.SolidLine)
        qpainter.setPen(pen)
        for i in range(0, SCREEN_INFO.width_cm):
            int_i = round(i * ppcm)
            qpainter.drawLine(int_i, 0, int_i, 20)
            metrics = qpainter.fontMetrics()
            fw = metrics.width(str(num_cm) + 'cm')
            qpainter.drawText(int_i - fw / 2, h * 2 / 3, str(num_cm) + 'cm')
            num_cm = num_cm + 1


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.initUI()

    def initUI(self):
        self.wid = RulerWidget()
        self._CloseButton = QPushButton("x")
        self._MinimumButton = QPushButton("-")
        self._MaximumButton = QPushButton("o")
        buttons = QHBoxLayout()
        buttons.addWidget(self._MinimumButton)
        buttons.addWidget(self._MaximumButton)
        buttons.addWidget(self._CloseButton)
        hbox = QHBoxLayout()
        hbox.addWidget(self.wid)
        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(buttons)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

        self.setGeometry(300, 300, 600, 210)
        self.setWindowTitle('Burning widget')
        self.show()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_drag = True
            self.m_DragPosition = event.globalPos() - self.pos()
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))

    def mouseMoveEvent(self, QMouseEvent):
        if Qt.LeftButton and self.m_drag:
            self.move(QMouseEvent.globalPos() - self.m_DragPosition)
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_drag = False
        self.setCursor(QCursor(Qt.ArrowCursor))

    def resizeEventX(self, QResizeEvent):
        self._TitleLabel.setFixedWidth(self.width())  # 将标题标签始终设为窗口宽度
        try:
            self._CloseButton.move(self.width() - self._CloseButton.width(), 0)
        except:
            pass
        try:
            self._MinimumButton.move(self.width() - (self._CloseButton.width() + 1) * 3 + 1, 0)
        except:
            pass
        try:
            self._MaximumButton.move(self.width() - (self._CloseButton.width() + 1) * 2 + 1, 0)
        except:
            pass

        # 重新调整边界范围以备实现鼠标拖放缩放窗口大小，采用三个列表生成式生成三个列表
        self._right_rect = [QPoint(x, y) for x in range(self.width() - self._padding, self.width() + 1)
                            for y in range(1, self.height() - self._padding)]
        self._bottom_rect = [QPoint(x, y) for x in range(1, self.width() - self._padding)
                             for y in range(self.height() - self._padding, self.height() + 1)]
        self._corner_rect = [QPoint(x, y) for x in range(self.width() - self._padding, self.width() + 1)
                             for y in range(self.height() - self._padding, self.height() + 1)]


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
