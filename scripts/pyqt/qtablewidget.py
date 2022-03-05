from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout
import sys


class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.title = "PyQt5 Tables"
        self.top = 100
        self.left = 100
        self.width = 500
        self.height = 400

        self.InitWindow()

    def InitWindow(self):
        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)

        self.creatingTables()

        self.show()

    def creatingTables(self):
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(5)
        self.tableWidget.setColumnCount(3)

        self.tableWidget.setItem(0, 0, QTableWidgetItem("Name"))
        self.tableWidget.setItem(0, 1, QTableWidgetItem("Email"))
        self.tableWidget.setItem(0, 2, QTableWidgetItem("Phone No"))

        self.tableWidget.setItem(1, 0, QTableWidgetItem("Parwiz"))
        self.tableWidget.setItem(1, 1, QTableWidgetItem("parwiz@gmail.com"))
        self.tableWidget.setItem(1, 2, QTableWidgetItem("845845845"))
        self.tableWidget.setColumnWidth(1, 200)

        self.tableWidget.setItem(2, 0, QTableWidgetItem("Ahmad"))
        self.tableWidget.setItem(2, 1, QTableWidgetItem("ahmad@gmail.com"))
        self.tableWidget.setItem(2, 2, QTableWidgetItem("2232324"))

        self.tableWidget.setItem(3, 0, QTableWidgetItem("John"))
        self.tableWidget.setItem(3, 1, QTableWidgetItem("john@gmail.com"))
        self.tableWidget.setItem(3, 2, QTableWidgetItem("2236786782324"))

        self.tableWidget.setItem(4, 0, QTableWidgetItem("Doe"))
        self.tableWidget.setItem(4, 1, QTableWidgetItem("Doe@gmail.com"))
        self.tableWidget.setItem(4, 2, QTableWidgetItem("12343445"))

        self.vBoxLayout = QVBoxLayout()
        self.vBoxLayout.addWidget(self.tableWidget)
        self.setLayout(self.vBoxLayout)


App = QApplication(sys.argv)
window = Window()
sys.exit(App.exec())

