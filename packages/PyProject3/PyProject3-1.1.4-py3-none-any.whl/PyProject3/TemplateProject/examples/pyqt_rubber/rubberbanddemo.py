import sys
from PyQt5.QtWidgets import QApplication, QWidget, QRubberBand, QCheckBox
from PyQt5.QtCore import QRect, QSize


class Demo(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(300, 300)
        for i in range(0, 30):
            cb = QCheckBox(self)
            cb.setText(str(i))
            cb.move(i % 4 * 50, i // 4 * 30)
            self.rb = QRubberBand(QRubberBand.Rectangle, self)  # 创建橡皮筋控件

    def mousePressEvent(self, event):  # 鼠标键按下时调用
        self.weizi = event.pos()
        self.rb.setGeometry(QRect(self.weizi, QSize()))
        self.rb.show()

    def mouseMoveEvent(self, event):  # 鼠标移动事件
        rect = QRect(self.weizi, event.pos()).normalized()
        self.rb.setGeometry(rect)
        # normalized()  使鼠标往下往上归一化，如果width<0 交换左右角；如果height<0,就交换顶角和底角
        # 我不理解的问题：QRect的第二个参数不是应该是矩形的width和height，event.pos()不是鼠标的位置吗，
        # 它不是宽和高，我认为应该减去原点才是宽和高啊？请理解的学友给我解释解释
        #
        # QRect的第二个参数可以是： QSize 或 QPoint

    def mouseReleaseEvent(self, event):  # 鼠标键释放时调用
        rect = self.rb.geometry()
        for child in self.children():
            if rect.contains(child.geometry()) and child.inherits('QCheckBox'):
                child.toggle()
            self.rb.hide()
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
