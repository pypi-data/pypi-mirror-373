import sys
from PyQt5 import QtCore, QtGui, uic
from PyQt5.QtWidgets import QApplication, QMainWindow
import myres_rc
from mainwindow import Ui_MainWindow
# qtMainFile = "mainwindow.ui"  # Enter file here.
# Ui_MainWindow, QtBaseClass = uic.loadUiType(qtMainFile)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.pushButton_3.clicked.connect(self.print)

    def print(self):
        print("hello world")


def main():
    app = QApplication(sys.argv)
    mywin = MainWindow()
    mywin.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
