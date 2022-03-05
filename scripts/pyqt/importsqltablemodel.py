import sys

from PyQt5.QtCore import QVariant, Qt
from PyQt5.QtSql import QSqlTableModel, QSqlDatabase
from PyQt5.QtWidgets import QApplication, QTableView, QLabel, QItemDelegate


class ImportSqlTableModel(QSqlTableModel):
    def __init__(self, *args, **kwargs):
        super(ImportSqlTableModel, self).__init__(*args, **kwargs)
        self.booleanSet = [4, 5, 6]  # column with checkboxes
        self.readOnlySet = [1]  # columns which must not be changed
        self.setTable("typeOfValue")
        self.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.select()

    def data(self, index, role=Qt.DisplayRole):
        value = super(ImportSqlTableModel, self).data(index)
        if index.column() in self.booleanSet:
            if role == Qt.CheckStateRole:
                return Qt.Unchecked if value == 2 else Qt.Checked
            else:
                return QVariant()
        return QSqlTableModel.data(self, index, role)

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False
        if index.column() in self.booleanSet:
            if role == Qt.CheckStateRole:
                val = 2 if value == Qt.Unchecked else 0
                return QSqlTableModel.setData(self, index, val, Qt.EditRole)
            else:
                return False
        else:
            return QSqlTableModel.setData(self, index, value, role)

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        if index.column() in self.booleanSet:
            return Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsEditable
        elif index.column() in self.readOnlySet:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled
        else:
            return QSqlTableModel.flags(self, index)


class ReadOnlyDelegate(QItemDelegate):
    def createEditor(self, parent, option, index):
        lb = QLabel(parent)
        return lb


if __name__ == '__main__':
    app = QApplication(sys.argv)

    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName("/path/of/your_database.db")
    if not db.open():
        sys.exit(-1)
    model = ImportSqlTableModel()
    w = QTableView()
    w.setModel(model)
    for col in model.booleanSet:
        w.setItemDelegateForColumn(col, ReadOnlyDelegate(w))
    w.show()
    sys.exit(app.exec_())