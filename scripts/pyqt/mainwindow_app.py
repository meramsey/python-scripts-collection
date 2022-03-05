#!/usr/bin/env python3
# encoding: utf-8
import os

from PyQt5 import uic, QtWidgets
import sys

qtCreatorFile = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "mainwindow.ui")  # Type your file path
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class build(Ui_MainWindow, QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)


def start():
    app = QtWidgets.QApplication(sys.argv)
    bld = build()
    bld.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    start()
