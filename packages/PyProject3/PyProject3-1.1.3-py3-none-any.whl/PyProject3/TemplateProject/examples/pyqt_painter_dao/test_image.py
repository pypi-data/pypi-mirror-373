from pyqt5extras import ImageBox
from PyQt5 import QtWidgets
import sys

app = QtWidgets.QApplication(sys.argv)
w = ImageBox()
w.show()

sys.exit(app.exec_())
