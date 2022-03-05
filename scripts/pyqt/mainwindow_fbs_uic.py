# from fbs_runtime.application_context import is_frozen
# from fbs_runtime.excepthook.sentry import SentryExceptionHandler
import os
import sys
import requests
from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication
from fbs_runtime.application_context.PyQt5 import ApplicationContext, \
    cached_property

target_db = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "wizardassistant.db")


class AppContext(ApplicationContext):
    def run(self):
        version = self.build_settings['version']
        QApplication.setApplicationName("Wizard Assistant")
        QApplication.setOrganizationName("Wizard Assistant")
        QApplication.setOrganizationDomain("wizardassistant.com")
        current_version = version
        self.main_window.setWindowTitle("Wizard Assistant v" + version)
        # current release version url
        current_release_url = 'https://wizardassistant.com/current_release.txt'

        def versiontuple(v):
            return tuple(map(int, (v.split("."))))

        try:
            # Parse current release version from url
            response = requests.get(current_release_url)
            current_release = response.text

            print('Current Version: ' + current_version)
            print('Current Release: ' + current_release)
            # Compare versions
            if versiontuple(current_release) > versiontuple(current_version):
                print('New Update Available: ' + current_release)
                self.main_window.setWindowTitle(
                    "Wizard Assistant v" + version + '| New Update Available: ' + current_release)
                self.main_window.set(
                    "Wizard Assistant v" + version + '| New Update Available: ' + current_release)
                update_available = True
            else:
                update_available = False
            print('Update Available:' + str(update_available))
        except:

            pass

        self.main_window.show()
        return self.app.exec_()

    @cached_property
    def main_window(self):
        return MainWindow(self)

    QApplication.setStyle("Fusion")
    #
    # # Now use a palette to switch to dark colors:
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, QColor(25, 25, 25))
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    QApplication.setPalette(palette)

    # @cached_property
    # def app_db(self):
    #     global target_db_path
    #     target_db_path = self.get_resource('wizardassistant.db')
    #     return QSqlDatabase(self.get_resource('wizardassistant.db'))

    # @cached_property
    # def app_style(self):
    #     # global stylesheet
    #     return QFile(self.get_resource('mystylesheet.css'))


qtCreatorFile = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "mainwindow.ui")  # Type your file path
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, ctx):
        super(MainWindow, self).__init__()
        self.ctx = ctx
        # def __init__(self, *args, **kwargs):
        #     super().__init__(*args, **kwargs)
        self.setupUi(self)
        # self.show()


import sys

if __name__ == '__main__':
    appctxt = AppContext()
    exit_code = appctxt.run()
    sys.exit(exit_code)
