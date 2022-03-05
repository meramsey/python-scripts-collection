# from fbs_runtime.application_context import is_frozen
# from fbs_runtime.excepthook.sentry import SentryExceptionHandler
import os
import sys
import requests
from PyQt5 import uic, QtWidgets
from pyqtgraph import PlotWidget
import pyqtgraph as pg
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication
from fbs_runtime.application_context.PyQt5 import ApplicationContext, \
    cached_property


class AppContext(ApplicationContext):
    def run(self):
        version = self.build_settings['version']
        QApplication.setApplicationName("App Name")
        QApplication.setOrganizationName("Some Corp")
        QApplication.setOrganizationDomain("example.com")
        current_version = version
        self.main_window.setWindowTitle("App Name v" + version)
        self.main_window.show()
        return self.app.exec_()

    @cached_property
    def main_window(self):
        return MainWindow(self)


qtCreatorFile = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "mainwindow.ui")  # Type your file path
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, ctx):
        super(MainWindow, self).__init__()
        self.ctx = ctx
        self.setupUi(self)

        # Put all your custom signals slots and other code here.


import sys

if __name__ == '__main__':
    appctxt = AppContext()
    exit_code = appctxt.run()
    sys.exit(exit_code)
