# -*- coding: utf-8 -*-

"""
尺子。
"""
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QSlider, QApplication,
                             QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QMenu)
from PyQt5.QtCore import QObject, Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QPainter, QFont, QColor, QPen, QCursor, QImage
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
        self._padding = 2
        self.color = QColor(255, 0, 0)
        self.space = 50
        self.initUI()
        # self.setMouseTracking(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.generateMenu)

    def initUI(self):
        self.setMinimumSize(300, 60)

    def paintEvent(self, e):
        qpainter = QPainter()
        qpainter.begin(self)
        self.drawWidget(qpainter)

        qpainter.end()
        self.setMouseTracking(True)

    def generateMenu(self, pos):
        menu = QMenu()
        item1 = menu.addAction('red')
        item2 = menu.addAction('yellow')
        item3 = menu.addAction('white')

        menu.addSeparator()
        item4 = menu.addAction('space-20')
        item5 = menu.addAction('space-50')

        action = menu.exec_(self.mapToGlobal(pos))
        if action == item1:
            self.color = QColor(255, 0, 0)
        if action == item2:
            self.color = QColor(0, 255, 0)
        if action == item3:
            self.color = QColor(255, 255, 255)

        if action == item4:
            self.space = 20
        if action == item5:
            self.space = 50
        self.repaint()

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
        ppcm = 50
        pen = QPen(QColor(200, 0, 0), 1, Qt.SolidLine)
        qpainter.setPen(pen)
        # qpainter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        for i in range(0, SCREEN_INFO.width_cm * 10):
            float_i = i * ppcm / 10
            print(float_i)
            int_i = round(float_i)
            qpainter.drawLine(float_i, 0, float_i, 5 if i % 5 != 0 else 10)
            num_mm = num_mm + 1

        num_cm = 0
        pen = QPen(QColor(200, 0, 0), 1, Qt.SolidLine)
        qpainter.setPen(pen)
        for i in range(0, SCREEN_INFO.width_cm):
            float_i = i * ppcm
            int_i = round(float_i)
            qpainter.drawLine(float_i, 0, float_i, 20)
            metrics = qpainter.fontMetrics()
            tick_str = str(num_cm*50) + 'px'
            fw = metrics.width(tick_str)
            qpainter.drawText(int_i - fw / 2, h * 2 / 3, tick_str)
            num_cm = num_cm + 1


class ResizeAbleMixin(object):
    def __init__(self):
        super(ResizeAbleMixin, self).__init__()
        self._padding = 20
        self.initDrag()

    def initDrag(self):
        # 设置鼠标跟踪判断扳机默认值
        self._move_drag = False
        self._corner_drag = False
        self._bottom_drag = False
        self._right_drag = False

    def mousePressEvent(self, event):
        print(event.y)
        if (event.button() == Qt.LeftButton) and (event.pos() in self._corner_rect):
            # 鼠标左键点击右下角边界区域
            self._corner_drag = True
            event.accept()
        elif (event.button() == Qt.LeftButton) and (event.pos() in self._right_rect):
            # 鼠标左键点击右侧边界区域
            self._right_drag = True
            event.accept()
        elif (event.button() == Qt.LeftButton) and (event.pos() in self._bottom_rect):
            # 鼠标左键点击下侧边界区域
            self._bottom_drag = True
            event.accept()
        elif (event.button() == Qt.LeftButton) and (event.y() < self.height()):
            # 鼠标左键点击标题栏区域
            self._move_drag = True
            self.move_DragPosition = event.globalPos() - self.pos()
            event.accept()
        else:
            pass

    def mouseMoveEvent(self, QMouseEvent):
        # 判断鼠标位置切换鼠标手势
        print('_corner_rect', self._corner_rect)
        print('_bottom_rect', self._bottom_rect)
        print('_right_rect', self._right_rect)
        print(QMouseEvent.pos())
        if QMouseEvent.pos() in self._corner_rect:
            print("pos in _corner_rect")
            self.setCursor(Qt.SizeFDiagCursor)
        elif QMouseEvent.pos() in self._bottom_rect:
            print("pos in _bottom_rect")
            self.setCursor(Qt.SizeVerCursor)
        elif QMouseEvent.pos() in self._right_rect:
            print("pos in _right_rect")
            self.setCursor(Qt.SizeHorCursor)
        else:
            print("pos in others")
            self.setCursor(Qt.OpenHandCursor)  # ArrowCursor
        # 当鼠标左键点击不放及满足点击区域的要求后，分别实现不同的窗口调整
        # 没有定义左方和上方相关的5个方向，主要是因为实现起来不难，但是效果很差，拖放的时候窗口闪烁，再研究研究是否有更好的实现
        print(Qt.LeftButton)
        print(self._right_drag)
        print(self._bottom_drag)
        print(self._corner_drag)
        print(self._move_drag)
        if Qt.LeftButton and self._right_drag:
            # 右侧调整窗口宽度
            self.resize(QMouseEvent.pos().x(), self.height())
            QMouseEvent.accept()
        elif Qt.LeftButton and self._bottom_drag:
            # 下侧调整窗口高度
            self.resize(self.width(), QMouseEvent.pos().y())
            QMouseEvent.accept()
        elif Qt.LeftButton and self._corner_drag:
            # 右下角同时调整高度和宽度
            self.resize(QMouseEvent.pos().x(), QMouseEvent.pos().y())
            QMouseEvent.accept()
        elif Qt.LeftButton and self._move_drag:
            # 标题栏拖放窗口位置
            print("moving")
            print(self.move_DragPosition)
            print(QMouseEvent.globalPos() - self.move_DragPosition)
            self.move(QMouseEvent.globalPos() - self.move_DragPosition)
            QMouseEvent.accept()
        print("mouse moved")

    def mouseReleaseEvent(self, QMouseEvent):
        self._move_drag = False
        self._corner_drag = False
        self._bottom_drag = False
        self._right_drag = False
        self.setCursor(QCursor(Qt.ArrowCursor))
        print(QMouseEvent.pos())
        print(self._corner_rect)

    def resizeEvent(self, QResizeEvent):
        # self._TitleLabel.setFixedWidth(self.width())  # 将标题标签始终设为窗口宽度
        # try:
        #     self._CloseButton.move(self.width() - self._CloseButton.width(), 0)
        # except:
        #     pass
        # try:
        #     self._MinimumButton.move(self.width() - (self._CloseButton.width() + 1) * 3 + 1, 0)
        # except:
        #     pass
        # try:
        #     self._MaximumButton.move(self.width() - (self._CloseButton.width() + 1) * 2 + 1, 0)
        # except:
        #     pass

        # 重新调整边界范围以备实现鼠标拖放缩放窗口大小，采用三个列表生成式生成三个列表
        self._right_rect = [QPoint(x, y) for x in range(self.width() - self._padding, self.width() + 1)
                            for y in range(1, self.height() - self._padding)]
        self._bottom_rect = [QPoint(x, y) for x in range(1, self.width() - self._padding)
                             for y in range(self.height() - self._padding, self.height() + 1)]
        self._corner_rect = [QPoint(x, y) for x in range(self.width() - self._padding, self.width() + 1)
                             for y in range(self.height() - self._padding, self.height() + 1)]


class MainRulerWindow(ResizeAbleMixin, QWidget):
    def __init__(self):
        super(MainRulerWindow, self).__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.initUI()
        self.setMouseTracking(True)

    def initUI(self):
        self.wid = RulerWidget()
        hbox = QHBoxLayout()
        hbox.addWidget(self.wid)
        vbox = QVBoxLayout()
        # vbox.addStretch(1)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

        self.setGeometry(0, 0, 500, 60)
        self.setWindowTitle('Burning widget')
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainRulerWindow()
    sys.exit(app.exec_())
