from qtpy.QtWidgets import QTabWidget, QPushButton
from qtpy import QtWidgets, QtGui, QtCore
#import gi
#from gi.repository import Wnck, Gdk
import time
import sys

class Container(QtWidgets.QTabWidget):
    def __init__(self):
        QtWidgets.QTabWidget.__init__(self)
        self.setDocumentMode(True)
        self.setTabPosition(QTabWidget.South)
        self._new_button = QPushButton(self)
        self._new_button.setText("New SSH Session")
        self.setCornerWidget(self._new_button)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.embed('xterm')

    def embed(self, command, *args):
        proc = QtCore.QProcess()
        proc.setProgram(command)
        proc.setArguments(args)
        #started, procId = proc.startDetached()
        #pid = None
        #started = proc.startDetached(pid)
        # https://stackoverflow.com/q/31519215 : "overload" startDetached : give three arguments, get a tuple(boolean,PID)
        # NB: we will get a failure `xterm: No absolute path found for shell: .` even if we give it an empty string as second argument; must be a proper abs path to a shell
        started, procId = proc.startDetached(command, ["/bin/bash"], ".")
        if not started:
            QtWidgets.QMessageBox.critical(self, 'Command "{}" not started!'.format(command), "Eh")
            return

        # attempts = 0
        # while attempts < 10:
        #     screen = Wnck.Screen.get_default()
        #     screen.force_update()
        #     # do a bit of sleep, else window is not really found
        #     time.sleep(0.1)
        #     # this is required to ensure that newly mapped window get listed.
        #     while Gdk.events_pending():
        #         Gdk.event_get()
        #     for w in screen.get_windows():
        #         print(attempts, w.get_pid(), procId, w.get_pid() == procId)
        #         if w.get_pid() == procId:
        #             self.window = QtGui.QWindow.fromWinId(w.get_xid())
        #             #container = QtWidgets.QWidget.createWindowContainer(window, self)
        #             proc.setParent(self)
        #             #self.scrollarea = QtWidgets.QScrollArea()
        #             #self.container = QtWidgets.QWidget.createWindowContainer(self.window)
        #             # via https://vimsky.com/zh-tw/examples/detail/python-method-PyQt5.QtCore.QProcess.html
        #             #pid = proc.pid()
        #             #win32w = QtGui.QWindow.fromWinId(pid) # nope, broken window
        #             win32w = QtGui.QWindow.fromWinId(w.get_xid()) # this finally works
        #             win32w.setFlags(QtCore.Qt.FramelessWindowHint)
        #             widg = QtWidgets.QWidget.createWindowContainer(win32w)
        #
        #             #self.container.layout = QtWidgets.QVBoxLayout(self)
        #             #self.addTab(self.container, command)
        #             self.addTab(widg, command)
        #             #self.scrollarea.setWidget(self.container)
        #             #self.container.setParent(self.scrollarea)
        #             #self.scrollarea.setWidgetResizable(True)
        #             #self.scrollarea.setFixedHeight(400)
        #             #self.addTab(self.scrollarea, command)
        #             self.resize(500, 400) # set initial size of window
        #             return
        #     attempts += 1
        QtWidgets.QMessageBox.critical(self, 'Window not found', 'Process started but window not found')


app = QtWidgets.QApplication(sys.argv)
w = Container()
w.show()
sys.exit(app.exec_())