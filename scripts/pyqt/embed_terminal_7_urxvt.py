import sys
from PyQt5 import QtCore, QtWidgets
import subprocess
import os


class EmbTerminal(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(EmbTerminal, self).__init__(parent)
        self.resize(1280, 720)
        self.process = QtCore.QProcess(self)
        self.terminal = QtWidgets.QWidget(self)
        layout = QtWidgets.QVBoxLayout(self)

        # Works also with urxvt:
        if subprocess.call(["which", 'xterm'], stdout=open(os.devnull, 'wb')) == 1:
            self.process.start('xterm', ['-into', str(int(self.winId()))])
        else:
            #self.process.start('xterm',['-into', str(int(self.winId()))])
            self.process.start('urxvt', ['-embed', str(int(self.winId()))])
        # self.setFixedSize(450, 340)
        #self.setGeometry(1, 1, 495, 325)
        #self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        layout.addWidget(self)
        self.setLayout(layout)
        #self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

    def close(self):
        self.process.kill()


class mainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(mainWindow, self).__init__(parent)

        central_widget = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        #tab_widget = QtWidgets.QTabWidget()
        lay.addWidget(EmbTerminal())
        #self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # self.setMinimumSize(450,340)

        # tab_widget.addTab(EmbTerminal(), "EmbTerminal")
        # tab_widget.addTab(QtWidgets.QTextEdit(), "QTextEdit")
    # tab_widget.addTab(QtWidgets.QMdiArea(), "QMdiArea")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main = EmbTerminal()
    main.show()
    sys.exit(app.exec_())