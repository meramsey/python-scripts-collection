# Get absolute path to current dir app is running from even when frozen
import os
import sys
from pathlib import Path

from PyQt5 import QtGui, uic, QtCore
from PyQt5.QtCore import QStandardPaths

app_path = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])))

# Create app icons path from above and setup lambda to make it easy to use
app_icon_path = os.path.join(app_path, 'images')
qIcon = lambda name: QtGui.QIcon(os.path.join(app_icon_path, name))

# Create ui files path from app path and setup lambda to make it easy to use
ui_dir = os.path.join(app_path, 'ui')
ui_path = lambda name: (os.path.join(ui_dir, name))
ui_loader = lambda name, parent: uic.loadUi(ui_path(name), parent)

app_settings = QtCore.QSettings('WizardAssistant', 'WizardAssistantDesktop')
config_data_dir = Path("WizardAssistant/WizardAssistantDesktop")

app_config_data_dir = QStandardPaths.writableLocation(
    QStandardPaths.AppConfigLocation) / config_data_dir

os.makedirs(app_config_data_dir, exist_ok=True)

DataDirPath = lambda name: app_config_data_dir / name

# wizard_cmd_db_merged = QStandardPaths.writableLocation(
#     QStandardPaths.AppConfigLocation) / config_data_dir / "wizardassistant-merged.db"

wizard_cmd_db_merged = DataDirPath('wizardassistant-merged.db')
