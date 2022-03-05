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

    for name, obj in dict(self.__dict__).items():
        # print(str(name) + str(obj))
        obj_type = str(obj).strip("<PyQt5").rsplit(" ")[0].replace(".", '', 1)
        # obj_type = str(obj).strip("<").rsplit(" ")[0]
        # print(obj_type)
        # obj_type = obj_str.strip("<PyQt5").rsplit(" ")[0].replace(".", '', 1)
        label_name = "self." + str(name)
        try:
            label_name = self.findChild(eval(obj_type), name)
            print(str(label_name) + ' created')
        except:
            pass
        if not isinstance(obj_type, QObject):
            continue


def start():
    app = QtWidgets.QApplication(sys.argv)
    bld = build()
    bld.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    start()
