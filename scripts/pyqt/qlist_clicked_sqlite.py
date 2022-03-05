import re
import sys
from datetime import date

from PySide2.QtCore import Qt
from qtpy import QtSql
from PySide2.QtSql import QSqlDatabase, QSqlQueryModel, QSqlQuery
from PySide2.QtWidgets import QTableView, QApplication
import sys

command_category = 'FirewallChecks'  # self.commandcategorydropdown


def replace(string, substitutions):
    substrings = sorted(substitutions, key=len, reverse=True)
    regex = re.compile('|'.join(map(re.escape, substrings)))
    return regex.sub(lambda match: substitutions[match.group(0)], string)


# domain = self.domaininput.text()
# url = self.urlinput.text()
# email = self.emailinput.text()
# email2 = self.emailinput2.text()
# username = self.usernameinput.text()
# clientip = self.clientipinput.text()
# date_time_input = self.dateTimeinput.text()

domain = 'wizardassistant.com'
url = 'https://wizardassistant.com'
email = 'admin@wizardassistant.com'
email2 = 'sales@wizardassistant.com'
username = 'cooluser666'
clientip = '192.168.10.12'
date_time_input = date.today()

# DomainInputField
# Email1InputField
# Email2InputField
# CPUsernameInputField
# ClientIPInputField
# DateTimeInputField

substitutions = {"DomainInputField": domain, "Email1InputField": email, "Email2InputField": email2,
                 "CPUsernameInputField": username, "ClientIPInputField": clientip,
                 "DateTimeInputField": date_time_input, }


def listclicked(index):
    row = index.row()
    print(row)
    cmd = model.data(row).field(3).value()
    # cmd = projectModel.data(projectModel.index(row, 3))
    print(cmd)
    cmd_replaced = replace(cmd, substitutions)
    # print(row)
    # print(cmd)
    print()
    # print("id = %s" % projectModel.record(row).field(0).value().toString())
    print("command = %s" % model.record(row).field(3).value())
    print("adjusted command = %s" % cmd_replaced)


app = QApplication(sys.argv)

db = QSqlDatabase.addDatabase("QSQLITE")
db.setDatabaseName("/home/user/PycharmProjects/WizardAssistantPython/wizardassistant.db")
if db.open():
    print('connect to SQL Server successfully')

else:
    print('connection failed')

model = QSqlQueryModel()
model.setQuery("SELECT command_alias, command FROM commands WHERE category = '%s'" % command_category)
# model.setHeaderData(0, Qt.Horizontal, tr("Name"))
# model.setHeaderData(1, Qt.Horizontal, tr("Salary"))


view = QTableView()
view.setModel(model)
view.hideColumn(1)  # hide id column
view.show()

db.close()

app.exec_()
