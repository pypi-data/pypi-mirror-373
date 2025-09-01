#!/usr/bin/env python
# coding=utf-8
# @Time    : 2020/10/19 16:19
# @Author  : 江斌
# @Software: PyCharm

import sys
from PyQt5.QtWidgets import *
from PyQt5 import QtGui, Qt, QtWidgets

PAGE_INTRO = 0
PAGE_INTRO2 = 1


class MyWizard(QWizard):
    def nextId(self):
        _id = self.currentId()
        print('aaaa')
        print(_id)
        if _id == PAGE_INTRO:
            print(self.field("className"))
            print(self.field("className"))
            print(self.field("className"))
            return PAGE_INTRO2
        else:
            return -1


class IntroWizardPage(QWizardPage):
    def __init__(self, parent):
        super(IntroWizardPage, self).__init__(parent)
        self.setTitle("Introduction")
        self.setSubTitle(
            "izards consist of a sequence of QWizardPage s. At any time, only one page is shown. A page has the following attributes")

        self.setPixmap(QWizard.WatermarkPixmap, QtGui.QPixmap(r"C:\Users\Admin\Pictures\zz.png"))
        self.setPixmap(QWizard.LogoPixmap, QtGui.QPixmap(r"C:\Users\Admin\Pictures\ue4.png"))
        self.setPixmap(QWizard.BannerPixmap, QtGui.QPixmap(r"C:\Users\Admin\Pictures\zzz.jpg"))
        classNameLabel = QLabel(self.tr("&Class name:"))
        classNameLineEdit = QLineEdit()
        classNameLabel.setBuddy(classNameLineEdit)

        baseClassLabel = QLabel(self.tr("B&ase class:"))
        baseClassLineEdit = QLineEdit()
        baseClassLabel.setBuddy(baseClassLineEdit)
        qobjectMacroCheckBox = QCheckBox(self.tr("Generate Q_OBJECT &macro"))
        layout = QGridLayout()
        layout.addWidget(classNameLabel, 0, 0)
        layout.addWidget(classNameLineEdit, 0, 1)
        layout.addWidget(baseClassLabel, 1, 0)
        layout.addWidget(baseClassLineEdit, 1, 1)
        layout.addWidget(qobjectMacroCheckBox, 2, 0)
        self.setLayout(layout)
        self.registerField("className*", classNameLineEdit)
        self.registerField("baseClass*", baseClassLineEdit)
        self.registerField("qobjectMacro", qobjectMacroCheckBox)


def test():
    app = QtWidgets.QApplication(sys.argv)
    wizard = MyWizard()
    wizard.setWizardStyle(QWizard.ClassicStyle)
    page1 = IntroWizardPage(wizard)
    page2 = QWizardPage()
    wizard.addPage(page1)
    wizard.addPage(page2)
    wizard.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    test()
