# imports
#from PyQt5 import QtWidgets, QtGui
import numpy as np
import pptk
#import win32gui
import sys

# local imports
#from designer import Ui_MainWindow

import sys
from PyQt5 import QtWidgets, QtGui
from mainwindow import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)

        self.cloudpoint = np.random.rand(100, 3)
        self.v = pptk.viewer(self.cloudpoint)                # generate the viewer window
        hwnd = win32gui.FindWindowEx(0, 0, None, "viewer")   # retrieve the window ID of the viewer
        self.window = QtGui.QWindow.fromWinId(hwnd)          # get the viewer inside a window

        # embed the window inside the centralwidget of the MainWindow :
        self.windowcontainer = self.createWindowContainer(self.window, self.centralwidget)

        # finally, resize the container as you wish.
        self.windowcontainer.resize(self.width() - 100 , self.height() - 100)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("fusion")
    form = MainWindow()
    form.show()
    sys.exit(app.exec_())