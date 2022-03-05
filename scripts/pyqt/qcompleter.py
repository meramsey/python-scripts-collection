import sys
import sqlite3
import time
import datetime
import platform
import os
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSql import QSqlDatabase
from PyQt5.QtWidgets import *
from PyQt5.uic.properties import QtGui

conn = sqlite3.connect('/home/user/PycharmProjects/WizardAssistant/src/main/python/wizardassistant.db')
c = conn.cursor()

target_db = '/home/user/PycharmProjects/WizardAssistant/src/main/python/wizardassistant.db'

# if platform == 'Windows':
#     target_db = (os.path.abspath(os.path.dirname(sys.argv[0])) + "\\" + "wizardassistant.db")
#
# if platform == 'Linux' or 'MAC':
#     target_db = (os.path.abspath(os.path.dirname(sys.argv[0])) + "/" + "wizardassistant.db")

target_db_path = target_db
print(target_db_path)

# Define App internal DB
db = QSqlDatabase.addDatabase("QSQLITE")
db.setDatabaseName(target_db_path)

target_db = target_db_path
sqliteConnection = sqlite3.connect(target_db)
cursor = sqliteConnection.cursor()
print("Connected to SQLite")


# def current_activated_category(self):
#     global command_category
#     command_category = str(self.commandcategorydropdown.currentText())
#     print(str(self.commandcategorydropdown.currentText()))
#     db.open()
#     self.commandslist.projectModel.setQuery(QtSql.QSqlQuery("SELECT command_alias, command FROM commands WHERE category = '%s'" % command_category))
#     self.commandslist.projectView = QListView(self.commandslist)
#     self.commandslist.projectView.setModel(self.commandslist.projectModel)
#     db.close()

class MainWindow(QMainWindow):

    # Defines Initial Window Settings
    def __init__(self):
        super(MainWindow, self).__init__()
        # self.setGeometry(650, 300, 500, 400) # window geometry
        self.home()

    def home(self):
        self.edit = QLineEdit(self)
        # self.edit.move(250, 250)
        self.completer = QCompleter()
        self.edit.setCompleter(self.completer)
        self.model = QStringListModel()
        self.completer.setModel(self.model)
        self.get_data()
        self.show()

    def get_data(self):
        c.execute("SELECT command_alias, command FROM commands")
        results = c.fetchall()
        new_list = [i[0] for i in results]
        print(new_list)  # Test print
        self.model.setStringList(new_list)  # From here up I was able to get the
        # code to work but there's no auto completion in the QLineEdit.


def run():
    app = QApplication(sys.argv)
    gui = MainWindow()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run()
