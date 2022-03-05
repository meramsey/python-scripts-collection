from PyQt5 import QtCore
from PyQt5.QtCore import QStandardPaths

# https://doc.qt.io/qtforpython/PySide2/QtCore/QStandardPaths.html#more
# print(str(QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation)))
# print(str(QStandardPaths.writableLocation(QStandardPaths.ConfigLocation)))
# print(str(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)))
# print(str(QStandardPaths.writableLocation(QStandardPaths.ConfigLocation)))

std_paths_list_names = ['QStandardPaths.DesktopLocation', 'QStandardPaths.DocumentsLocation',
                        'QStandardPaths.FontsLocation', 'QStandardPaths.ApplicationsLocation',
                        'QStandardPaths.MusicLocation', 'QStandardPaths.MoviesLocation',
                        'QStandardPaths.PicturesLocation', 'QStandardPaths.TempLocation', 'QStandardPaths.HomeLocation',
                        'QStandardPaths.DataLocation', 'QStandardPaths.CacheLocation',
                        'QStandardPaths.GenericCacheLocation', 'QStandardPaths.GenericDataLocation',
                        'QStandardPaths.RuntimeLocation', 'QStandardPaths.ConfigLocation',
                        'QStandardPaths.DownloadLocation', 'QStandardPaths.GenericConfigLocation',
                        'QStandardPaths.AppDataLocation', 'QStandardPaths.AppLocalDataLocation',
                        'QStandardPaths.AppConfigLocation']
std_paths_list = [QStandardPaths.DesktopLocation, QStandardPaths.DocumentsLocation, QStandardPaths.FontsLocation,
                  QStandardPaths.ApplicationsLocation, QStandardPaths.MusicLocation, QStandardPaths.MoviesLocation,
                  QStandardPaths.PicturesLocation, QStandardPaths.TempLocation, QStandardPaths.HomeLocation,
                  QStandardPaths.DataLocation, QStandardPaths.CacheLocation, QStandardPaths.GenericCacheLocation,
                  QStandardPaths.GenericDataLocation, QStandardPaths.RuntimeLocation, QStandardPaths.ConfigLocation,
                  QStandardPaths.DownloadLocation, QStandardPaths.GenericConfigLocation, QStandardPaths.AppDataLocation,
                  QStandardPaths.AppLocalDataLocation, QStandardPaths.AppConfigLocation]

for path in std_paths_list:
    details = f"""path: {str(path)} : location : {str(QStandardPaths.writableLocation(path))}"""
    print(details)

print(str(QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation)))
