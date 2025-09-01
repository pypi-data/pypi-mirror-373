import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLineEdit, QMdiSubWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl


class WebEngineView(QWebEngineView):
    windowList = []

    def __init__(self, parent=None):
        super(WebEngineView, self).__init__()
        self.parent = parent
        self.urlChanged.connect(self.onUrlChanged)

    def createWindow(self, QWebEnginePage_WebWindowType):
        new_webview = WebEngineView()
        new_window = BrowserWidget(new_webview)
        if BrowserWidget.MainWindow:
            sub = QMdiSubWindow()
            sub.setWidget(new_window)
            BrowserWidget.MainWindow.count = BrowserWidget.MainWindow.count + 1
            sub.setWindowTitle("subwindow" + str(BrowserWidget.MainWindow.count))
            BrowserWidget.MainWindow.mdi.addSubWindow(sub)
            sub.show()
        else:
            new_window.show()
        new_webview.parent = new_window
        self.windowList.append(new_window)
        return new_webview

    def onUrlChanged(self, url):
        self.parent.set_url(url)


class BrowserWidget(QWidget):
    """  """
    MainWindow = None

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
        self.init_ui()

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

    def visit(self):
        url = self.url
        if not url.lower().startswith('http://') \
                and not url.lower().startswith('https://'):
            url = 'http://{}'.format(url)
        self.web_view.load(QUrl(url))

    def set_url(self, url):
        url = url.toString()
        self.url_text.setText(url)

def main():
    app = QApplication(sys.argv)
    win = BrowserWidget()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
