from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys


class ResizeAbleMixin(object):
    def __init__(self):
        super(ResizeAbleMixin, self).__init__()
        self._padding = 20
        self.initDrag()

    def initDrag(self):
        self._move_drag = False
        self._corner_drag = False
        self._bottom_drag = False
        self._right_drag = False

    def mousePressEvent(self, event):
        print(event.y)
        if (event.button() == Qt.LeftButton) and (event.pos() in self._corner_rect):  # 鼠标左键点击右下角边界区域
            self._corner_drag = True
            event.accept()
        elif (event.button() == Qt.LeftButton) and (event.pos() in self._right_rect):

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


class DaoGui(QWidget):
    def __init__(self, *args, **kwargs):
        super(DaoGui, self).__init__(*args, **kwargs)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.initUI()

    def initUI(self):
        self.setGeometry(QRect(0, 0, 200, 200))

    def paintEvent(self, e):
        qpainter = QPainter()
        qpainter.begin(self)
        self.drawWidget(qpainter)
        qpainter.end()

    def drawWidget(self, qpainter):

        pen = QPen(QColor(0, 255, 0), 1, Qt.SolidLine)
        size = self.size()
        w = size.width()
        h = size.height()
        qpainter.setPen(pen)
        qpainter.setBrush(QColor(0, 175, 175, 100))
        qpainter.drawRect(0, 0, w - 1, h - 1)
        qpainter.setFont(QFont('Arial', 20))
        content = " "
        metrics = qpainter.fontMetrics()
        dt = QDateTime.currentDateTime()
        dts = dt.toString('yyyy-MM-dd hh:mm:ss')
        fw1 = metrics.width(content)
        fw2 = metrics.width(dts)
        self.setGeometry(QRect(0, 0, max(fw1, fw2) * 1.5, h))
        qpainter.drawText(10, 20, dts)
        qpainter.drawText(10, 60, content)


class DaoTimer(object):
    def __init__(self, obj):
        self.timer = QTimer(obj)
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)  # 触发的时间间隔为1秒。
        self.obj = obj

    def update(self):
        self.obj.update()


class DaoMainWindow(ResizeAbleMixin, QWidget):
    def __init__(self):
        super(DaoMainWindow, self).__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.initUI()
        self.timer = DaoTimer(self.wid)
        self.setMouseTracking(True)

    def initUI(self):
        self.wid = DaoGui()
        hbox = QHBoxLayout()
        hbox.addWidget(self.wid)
        # vbox = QVBoxLayout()
        # vbox.addLayout(hbox)
        self.setLayout(hbox)
        self.setGeometry(0, 0, 500, 200)
        self.setWindowTitle('dao')
        self.show()


def main():
    app = QApplication(sys.argv)
    win = DaoMainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
