# -*- coding: utf-8 -*-
import atexit

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication, QWidget

class XTerm(QWidget):

    def __init__(self, parent, xterm_cmd="xterm"):
        QWidget.__init__(self, parent)
        self.xterm_cmd = xterm_cmd
        self.process = QProcess(self)
        self.connect(self.process,
                     pyqtSignal("finished(int, QProcess::ExitStatus)"),
                     self.on_term_close)
        atexit.register(self.kill)

    def kill(self):
        self.process.kill()
        self.process.waitForFinished()

    def sizeHint(self):
        size = QSize(400, 300)
        return size.expandedTo(QApplication.globalStrut())

    def show_term(self):
        args = [
            "-into",
            str(self.winId()),
            "-bg",
            "#000000",  # self.palette().color(QPalette.Background).name(),
            "-fg",
            "#f0f0f0",  # self.palette().color(QPalette.Foreground).name(),
            # border
            "-b", "0",
            "-w", "0",
            # blink cursor
            "-bc",
        ]
        self.process.start(self.xterm_cmd, args)
        if self.process.error() == QProcess.FailedToStart:
            print("xterm not installed")

    def on_term_close(self, exit_code, exit_status):
        print("close", exit_code, exit_status)
        self.close()

main_frame = XTerm()
main_frame.show()