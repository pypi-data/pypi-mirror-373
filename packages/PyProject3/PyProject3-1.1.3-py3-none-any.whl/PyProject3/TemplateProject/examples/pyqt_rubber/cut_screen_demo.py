import os
import sys
import time
import random
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtGui, QtCore
from system_hotkey import SystemHotkey
from PyQt5.QtWinExtras import QWinThumbnailToolBar, QWinThumbnailToolButton

hk = SystemHotkey()


class Trans(QWidget):
    closeCutScreenSignal = pyqtSignal()

    def __init__(self):
        super(Trans, self).__init__()
        self.cutPic = True
        self.screen = QApplication.primaryScreen()
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        pal = QPalette()
        pal.setBrush(QPalette.Highlight, QBrush(QtCore.Qt.green))
        self.rubberBand.setPalette(pal)

        self.setCursor(QtCore.Qt.CrossCursor)
        button = QPushButton('Close', self)
        self.initUI()

    def initUI(self):
        # self.setAttribute(QtCore.Qt.WA_NoSystemBackground, False)
        # self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

    def cutP(self, event=None):
        if not self.isActiveWindow():
            self.activateWindow()
            print(self.isActiveWindow(), self.isMinimized())
            if self.isMinimized():
                self.showMaximized()
        self.rubberBand.close()
        self.cutPic = True
        self.setCursor(QtCore.Qt.CrossCursor)

    def mousePressEvent(self, event):
        if self.cutPic:
            self.old = event.globalPos()
            self.old.x, self.old.y = self.old.x(), self.old.y()
        else:
            self.rubberBand.close()
            self.closeCutScreenSignal.emit()

    def mouseMoveEvent(self, event):
        if self.cutPic:
            self.new = event.globalPos()
            self.new.x, self.new.y = self.new.x(), self.new.y()
            self.rect = QtCore.QRect(QPoint(self.old.x, self.old.y), QPoint(self.new.x, self.new.y))
            self.rubberBand.setGeometry(self.rect)
            self.rubberBand.show()

    def mouseReleaseEvent(self, event):
        if self.cutPic:
            self.setCursor(QtCore.Qt.ArrowCursor)
            self.new = event.globalPos()
            self.new.x, self.new.y = self.new.x(), self.new.y()
            self.cutPic = False
            self.rect = QtCore.QRect(QPoint(self.old.x, self.old.y), QPoint(self.new.x, self.new.y))
            self.setWindowOpacity(0.01)
            self.screenshot = self.screen.grabWindow(QApplication.desktop().winId(), self.rect.x(), self.rect.y(),
                                                     self.rect.width(), self.rect.height())
            self.rubberBand.setGeometry(self.rect)
            self.rubberBand.show()
            # save
            dt = 'pic'
            while 1:
                n = random.randint(0, 10)
                dt += str(n)
                if n == 5:
                    break
            clipboard = QApplication.clipboard()
            clipboard.setPixmap(self.screenshot)  # 拷贝到剪切板
            self.screenshot.save('cut.png', 'png')
            self.rubberBand.close()
            self.close()


def test(event=None):
    app = QApplication(sys.argv)
    trans = Trans()
    trans.showFullScreen()
    trans.setWindowOpacity(0.4)
    trans.raise_()
    trans.show()
    app.exec_()


def open_root(e):
    p = os.path.abspath('.')
    os.startfile(p)


if __name__ == '__main__':
    hk.register(('control', 'alt', 'a'), callback=test)
    hk.register(('control', 'alt', 'p'), callback=open_root)
    print("截屏：CTRL+ALT+A\n 打开目录：CTRL+ALT+P")
    while True:
        time.sleep(1)
    # sys.exit()
