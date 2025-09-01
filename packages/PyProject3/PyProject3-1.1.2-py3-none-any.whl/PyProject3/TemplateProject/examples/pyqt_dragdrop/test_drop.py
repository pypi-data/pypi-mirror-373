import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from pyqt5Custom import DragDropFile


class Button(QPushButton):
    def __init__(self, title, parent):
        super().__init__(title, parent)
        self.setAcceptDrops(True)


class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setAcceptDrops(True)

    def initUI(self):
        self.setWindowIcon(QIcon('ringtones.ico'))
        label = QLabel("hello", self)
        label.move(30, 10)
        label.setOpenExternalLinks(True)
        label.setText("<a href='http://www.baidu.com' style='color:red;'>baidu<a>")
        edit = QLineEdit("", self)
        edit.setDragEnabled(True)
        edit.move(30, 65)

        button = Button("Button", self)
        button.move(190, 65)

        self.setWindowTitle("Simple drag & drop")
        self.setGeometry(300, 300, 300, 150)
        self.show()

    def dragEnterEvent(self, e):
        self.setStyleSheet("background-color:#aaa;")
        mime_data = e.mimeData()
        if mime_data.hasUrls:
            for url in mime_data.urls():
                print('drag enter: ', url.toLocalFile())
            e.accept()
            return
        if mime_data.hasFormat("text/plain"):
            e.accept()
        else:
            e.ignore()

    def dragLeaveEvent(self, e):
        self.setStyleSheet("")

    def dropEvent(self, e):
        self.setStyleSheet("")
        # self.setText(e.mimeData().text())
        mime_data = e.mimeData()
        clipboard = QApplication.clipboard()
        # mimeData = clipboard.mimeData()

        for url in mime_data.urls():
            clipboard.setText(url.toString())
            print('drop event: ', url.toString(), url.toLocalFile())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
