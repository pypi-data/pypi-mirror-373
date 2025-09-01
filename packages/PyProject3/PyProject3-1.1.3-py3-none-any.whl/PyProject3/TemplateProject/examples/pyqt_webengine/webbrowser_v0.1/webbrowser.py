import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, \
    QVBoxLayout, QPushButton, QLineEdit, QMdiSubWindow, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl


class WebEngineView(QWebEngineView):
    """  """

    def __init__(self, parent=None):
        super(WebEngineView, self).__init__()
        self.parent = parent  # parent是一个BrowserWidget
        self.urlChanged.connect(self.onUrlChanged)

    def createWindow(self, QWebEnginePage_WebWindowType):
        new_webview = WebEngineView()
        new_window = BrowserWidget(new_webview)
        # self.windowList.append(new_window)
        return new_webview

    def onUrlChanged(self, url):
        self.parent.set_url(url)


class BrowserWidget(QWidget):
    """  """
    MainWindow = None
    windowList = []

    def __init__(self, web_view=None):
        """
        运行弹窗新窗口。
        :param web_view:
        """
        super(BrowserWidget, self).__init__()
        self.url = "http://www.baidu.com"
        if web_view is None:
            self.is_new_window = False
            self.web_view = WebEngineView(self)
        else:
            self.is_new_window = True
            self.web_view = web_view
            self.web_view.parent = self
        self.init_ui()
        self.update_parent()
        self.windowList.append(self)
        print("window count:", self.windowList.__len__())

    def init_ui(self):
        self.setGeometry(100, 100, 600, 600)
        self.setWindowTitle('Web页面中的JavaScript与 QWebEngineView交互例子')
        layout = QVBoxLayout()
        self.nav_layout = QHBoxLayout()
        self.button = QPushButton('访问')
        self.url_text = QLineEdit(self.url)
        self.button.clicked.connect(self.visit)
        self.nav_layout.addWidget(self.url_text)
        self.nav_layout.addWidget(self.button)
        layout.addLayout(self.nav_layout)
        layout.addWidget(self.web_view)
        self.setLayout(layout)
        # self.show()
        if not self.is_new_window:
            self.visit()

    def update_parent(self):
        if BrowserWidget.MainWindow:
            sub = QMdiSubWindow()
            sub.setWidget(self)
            BrowserWidget.MainWindow.count = BrowserWidget.MainWindow.count + 1
            sub.setWindowTitle("subwindow" + str(BrowserWidget.MainWindow.count))
            BrowserWidget.MainWindow.mdi.addSubWindow(sub)
            sub.show()
        else:
            self.show()

    def visit(self):
        url = self.url
        if not url.lower().startswith('http://') \
                and not url.lower().startswith('https://'):
            url = 'http://{}'.format(url)
        self.web_view.load(QUrl(url))

    def set_url(self, url):
        """ 设置url """
        url = url.toString()
        self.url_text.setText(url)

    # 添加中文的确认退出提示框1
    def closeEvent(self, event):
        print("close it")

        for (idx, item) in enumerate(self.windowList):
            if item == self:
                current = idx
                break
        self.windowList.pop(current)
        event.accept()
        print("count: ", len(self.windowList))
        return

    def closeEvent2(self, event):
        quitMsgBox = QMessageBox()
        quitMsgBox.setWindowTitle('确认提示')
        quitMsgBox.setText('你确认退出吗？')
        quitMsgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        buttonY = quitMsgBox.button(QMessageBox.Yes)
        buttonY.setText('确定')
        buttonN = quitMsgBox.button(QMessageBox.No)
        buttonN.setText('取消')
        quitMsgBox.exec_()
        # 判断返回值，如果点击的是Yes按钮，我们就关闭组件和应用，否则就忽略关闭事件
        if quitMsgBox.clickedButton() == buttonY:
            event.accept()
        else:
            event.ignore()


def main():
    app = QApplication(sys.argv)
    win = BrowserWidget()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
