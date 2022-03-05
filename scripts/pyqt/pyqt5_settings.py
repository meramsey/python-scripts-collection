import sys

from PyQt5 import QtCore
import os

settings = QtCore.QSettings('WizardAssistant', 'WizardAssistantDesktop')
print(settings.fileName())
settings.setValue('wizardwebsshport', 8889)
# settings.setValue('theme_selection', 'Dark')
# settings.setValue('license', 'XXXX-XXXX-XXXX-XXXX')
# settings.remove('license')
settings.remove('panel_name')
keys = settings.allKeys()

# print(os.path.abspath(os.path.dirname(sys.argv[0])))
# print(os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'ui', "about.ui"))


print(keys)
print(settings.value('panel_name'))
