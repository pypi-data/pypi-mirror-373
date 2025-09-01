#!/usr/bin/env python
# coding=utf-8
# @Time    : 2020/10/10 15:52
# @Author  : 江斌
# @Software: PyCharm

'''
Created on 2013-7-2
@author: badboy
Email:lucky.haiyu@gmail.com
QQ:43831266
'''
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import math


class ResizeAbleMixin(object):
    def __init__(self, parent=None):
        super(ResizeAbleMixin, self).__init__()
        self._padding = 50
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
        # 重新调整边界范围以备实现鼠标拖放缩放窗口大小，采用三个列表生成式生成三个列表
        self._right_rect = [QPoint(x, y) for x in range(self.width() - self._padding, self.width() + 1)
                            for y in range(1, self.height() - self._padding)]
        self._bottom_rect = [QPoint(x, y) for x in range(1, self.width() - self._padding)
                             for y in range(self.height() - self._padding, self.height() + 1)]
        self._corner_rect = [QPoint(x, y) for x in range(self.width() - self._padding, self.width() + 1)
                             for y in range(self.height() - self._padding, self.height() + 1)]


class clockForm(ResizeAbleMixin, QWidget):
    def __init__(self, parent=None):
        super(clockForm, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle("Clock")
        # self.d = QComboBox( )
        # self.d.addItems(['hello', 'world'])
        # layout = QHBoxLayout()
        # layout.addWidget(self.d)
        # self.setLayout(layout)
        self.setGeometry(100, 100, 200, 200)
        self.timer = QTimer()
        # 设置窗口计时器
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.generateMenu)

        self.setMouseTracking(True)
    def generateMenu(self, pos):
        print('generateMenu')
        menu = QMenu()
        item1 = menu.addAction('China')
        menu.addSeparator()
        item2 = menu.addAction('USA')

        action = menu.exec_(self.mapToGlobal(pos))
        if action == item1:
            self.color = QColor(255, 0, 0)
        if action == item2:
            self.color = QColor(0, 255, 0)
        self.repaint()

    def paintEvent(self, event):
        super().update()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # 设置表盘中的文字字体
        font = QFont("Times", 6)
        fm = QFontMetrics(font)
        fontRect = fm.boundingRect("99")  # 获取绘制字体的矩形范围

        # 分针坐标点
        minPoints = [QPointF(50, 25),
                     QPointF(48, 50),
                     QPointF(52, 50)]

        # 时钟坐标点
        hourPoints = [QPointF(50, 35),
                      QPointF(48, 50),
                      QPointF(52, 50)]

        side = min(self.width(), self.height())
        side = side - 20
        painter.setViewport((self.width() - side) / 2, (self.height() - side) / 2, side, side)  # 始终处于窗口中心位置显示

        # painter.setViewport(QRect(0, 0, 50, 50))
        # 设置QPainter的坐标系统，无论窗体大小如何变化，
        # 窗体左上坐标为(0,0),右下坐标为(100,100),
        # 因此窗体中心坐标为(50,50)
        painter.setWindow(0, 0, 100, 100)

        # 绘制表盘，使用环形渐变色
        niceBlue = QColor(200, 200, 200)
        haloGrident = QRadialGradient(50, 50, 50, 50, 50)
        haloGrident.setColorAt(0.0, Qt.lightGray)
        # haloGrident.setColorAt(0.5, Qt.darkGray)
        # haloGrident.setColorAt(0.9, Qt.white)
        haloGrident.setColorAt(1.0, niceBlue)
        painter.setBrush(haloGrident)
        painter.setPen(QPen(Qt.darkGray, 1))
        painter.drawEllipse(0, 0, 100, 100)

        transform = QTransform()
        transform2 = QTransform()

        painter.setPen(QPen(Qt.black, 1.5))
        font2 = QFont("Colonna MT", 7)
        painter.setFont(font2)
        fm = QFontMetrics(font2)
        fontRect2 = fm.boundingRect("TISSOT")  # 获取绘制字体的矩形范围
        fontRect2.moveCenter(QPoint(50, 20 + fontRect.height() / 2))
        painter.drawText(fontRect2, Qt.AlignHCenter | Qt.AlignTop, "TISSOT")

        font = QFont("Arial", 4)
        painter.setFont(font)
        fm = QFontMetrics(font)
        fontRect2 = fm.boundingRect("1853")  # 获取绘制字体的矩形范围
        fontRect2.moveCenter(QPoint(50, 25 + fontRect.height() / 2))
        painter.drawText(fontRect2, Qt.AlignHCenter | Qt.AlignTop, "1853")

        # 绘制时钟为0的字，以及刻度
        painter.setPen(QPen(Qt.darkGray, 1.5))
        fontRect.moveCenter(QPoint(50, 10 + fontRect.height() / 2))
        painter.setFont(font)
        painter.drawLine(50, 2, 50, 8)  #
        painter.drawText(QRectF(fontRect), Qt.AlignHCenter | Qt.AlignTop, "12")
        fontRect.moveCenter(QPoint(50, 14 + fontRect.height() / 2))
        current_time = QTime().currentTime()
        hour_offset = 0 if current_time.hour() < 12 else 12
        # painter.drawText(QRectF(fontRect), Qt.AlignHCenter | Qt.AlignTop, ampm)
        painter.drawRect(QRectF(100, 45, 5, 10))
        for i in range(1, 12):
            transform.translate(50, 50)
            transform.rotate(30)
            transform.translate(-50, -50)
            painter.setWorldTransform(transform)
            painter.drawLine(50, 2, 50, 10)
            transform2.reset()
            transform2.translate(50, 50)
            painter.setWorldTransform(transform2)
            theta = (270 + i * 30) / 180 * math.pi
            fontRect.moveCenter(QPoint(35 * math.cos(theta), 35 * math.sin(theta)))
            painter.drawText(QRectF(fontRect), Qt.AlignHCenter | Qt.AlignTop, "%d" % (i+hour_offset))

        transform.reset()

        # 绘制分钟刻度线
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        for i in range(1, 60):
            transform.translate(50, 50)
            transform.rotate(6)
            transform.translate(-50, -50)
            if i % 5 != 0:
                painter.setWorldTransform(transform)
                if i in (28, 29, 31, 32):
                    transform2.reset()
                    transform2.translate(50, 50)
                    transform2.rotate(-180+i*6+6)
                    transform2.translate(-50, -50)
                    painter.setTransform(transform2)
                    if i == 28:
                        font = QFont('Corbel',  3)
                        painter.setFont(font)
                        painter.drawText(QRectF(47, 94, 47,   85), 'MADE')
                    if i == 31:
                        font = QFont('Corbel',  3)
                        painter.setFont(font)
                        # painter.drawText(QRectF(47, 0, 47,   15), 'swiss')
                        painter.drawText(QRectF(47, 94, 47,   85), 'SWISS')
                else:
                    painter.drawLine(50, 2, 50, 5)



        transform.reset()

        # 获取当前时间
        currentTime = QTime().currentTime()
        hour = currentTime.hour() if currentTime.hour() < 12 else currentTime.hour() - 12
        minite = currentTime.minute()
        second = currentTime.second()

        # 获取所需旋转角度
        hour_angle = hour * 30.0 + (minite / 60.0) * 30.0
        minite_angle = (minite / 60.0) * 360.0
        second_angle = second * 6.0

        # 时针
        transform.translate(50, 50)
        transform.rotate(hour_angle)
        transform.translate(-50, -50)
        painter.setWorldTransform(transform)
        painter.setPen(Qt.NoPen)
        # painter.setBrush(QBrush(Qt.darkRed))
        painter.setBrush(QBrush(QColor(100, 100, 100)))
        painter.drawPolygon(QPolygonF(hourPoints))

        transform.reset()

        # 分针
        transform.translate(50, 50)
        transform.rotate(minite_angle)
        transform.translate(-50, -50)
        painter.setWorldTransform(transform)
        # painter.setBrush(QBrush(Qt.darkGreen))
        painter.setBrush(QBrush(QColor(100, 100, 100)))
        painter.drawPolygon(QPolygonF(minPoints))

        transform.reset()
        # 秒针
        transform.translate(50, 50)
        transform.rotate(second_angle)
        transform.translate(-50, -50)
        painter.setWorldTransform(transform)
        # painter.setPen(QPen(Qt.darkCyan, 1))
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        painter.drawLine(50, 60, 50, 20)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    form = clockForm()
    form.show()
    app.exec_()
