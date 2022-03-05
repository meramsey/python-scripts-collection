import sys

from PyQt5 import QtWidgets, QtGui, QtCore

app = QtWidgets.QApplication(sys.argv)
win = QtWidgets.QWidget()
winID = int(win.winId())
sub_win = QtGui.QWindow.fromWinId(winID)
container = QtWidgets.QWidget.createWindowContainer(sub_win)
sub_win_id = int(container.winId())
process = QtCore.QProcess(container)
process.start('terminus')
win.show()
app.exec_()