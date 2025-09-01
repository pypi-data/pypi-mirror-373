# -*- coding: utf-8 -*-
"""
File Name  windows_gui
"""
import sys
import matplotlib
import numpy as np
from PyQt5 import uic
from PyQt5 import QtGui, QtWidgets, QtCore

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEngineScript, QWebEnginePage

zhfont1 = matplotlib.font_manager.FontProperties(fname="C:\Windows\Fonts\Deng.ttf")
zhfont1._size = 18
plt.rcParams['axes.titlesize'] = 18


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        ui_file = r"mdi_window_demo.ui"
        self.ui = uic.loadUi(ui_file, self)
        self.tabifyDockWidget(self.dockWidget_5, self.dockWidget_6)
        self.mdi = QtWidgets.QMdiArea()

        self.window1 = QtWidgets.QMainWindow()
        self.window2 = QtWidgets.QMainWindow()
        self.window3 = QtWidgets.QMainWindow()
        self.figure1 = plt.figure()
        self.figure2 = plt.figure()
        self.canvas1 = FigureCanvas(self.figure1)
        self.canvas2 = FigureCanvas(self.figure2)

        self.init_windows()
        self.init_buttons()

    def disp(self, msg, end="\n", clear_buffer=False):
        s = self.textEdit.toPlainText()
        if clear_buffer:
            self.textEdit.setText(msg + end)
        else:
            self.textEdit.setText(s + msg + end)

    def init_windows(self):
        self.window1.setWindowTitle('window1')
        self.window2.setWindowTitle('window2')
        self.mdiArea.addSubWindow(self.window1)
        self.mdiArea.addSubWindow(self.window2)
        self.mdiArea.addSubWindow(self.window3)
        self.mdi.tileSubWindows()

        ax = self.figure1.add_axes([0.1, 0.1, 0.8, 0.8])
        ax.plot([1, 2, 3, 4, 3, 2, 2, 1, 21, 341, 12])
        self.canvas1.draw()
        self.window1.setCentralWidget(self.canvas1)
        with plt.style.context('dark_background'):
            pass
        ax = self.figure2.add_axes([0.15, 0.1, 0.8, 0.8])
        x = np.linspace(0, 4 * 3.14, 100)
        y = np.sin(x)
        ax.plot(x, y, 'gx-')
        ax.set_xlabel("t/s")
        ax.set_ylabel("height/m")
        ax.set_title("测试", fontproperties=zhfont1, fontdict={'fontsize': 18})
        ax.legend()
        ax.grid('on')
        ax.set_facecolor('#000000')

        self.canvas2.draw()
        self.window2.setCentralWidget(self.canvas2)
        self.disp("init windows", clear_buffer=True)

        web_view = QWebEngineView()
        web_view.load(QtCore.QUrl("http://www.baidu.com"))
        self.window3.setCentralWidget(web_view)

    def init_buttons(self):
        self.pushButton.clicked.connect(self.on_show_all)
        self.pushButton_2.clicked.connect(self.on_btn2)
        self.disp("init buttons")

    def on_show_all(self):
        print("on show all")
        self.window1.show()
        self.window2.show()

    def plot2(self):
        ax = self.figure.add_axes([0.1, 0.1, 0.8, 0.8])
        ax.plot([100, 2, 3, 4, 341, 12])
        self.canvas.draw()

    def on_btn2(self):
        # sublist = self.mdiArea.subWindowList()
        pass
        cmd = self.textEdit_2.toPlainText()
        try:
            self.disp("========cmd=======")
            self.disp(cmd)
            eval(cmd)
        except Exception as e:
            self.disp(str(e))


def main():
    s = '''
    
/*ToolBox*/
QToolBox{
background-color: rgb(80, 80, 80);/*背景色-空隙颜色*/
border:1px solid rgb(128, 128, 128);
}
QToolBox QWidget{/*tab页*/
background-color: rgb(80, 80, 80);
}
QToolBox>QAbstractButton{/*标题栏*/
min-height:30px;
}
QToolBox::tab{
background-color:rgb(40, 40, 40);
}
QToolBox::tab:hover{
color:black;
background-color: rgb(255, 170, 0);
}
QToolBox::tab:selected{
color:rgb(255, 170, 0);
}
QToolBox::tab:selected:hover{
color:black;
} '''
    app = QtWidgets.QApplication(sys.argv)
    # app.setStyleSheet(open('nodeeditor-dark.qss').read())
    app.setStyleSheet(s)
    win = MainWindow()
    win.show()
    ret = app.exec_()
    sys.exit(ret)


if __name__ == '__main__':
    main()
