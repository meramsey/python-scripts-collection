#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5.QtWidgets import QCompleter, QComboBox


class ExtendedComboBox(QComboBox):
    def __init__(self, parent=None):
        super(ExtendedComboBox, self).__init__(parent)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setEditable(True)

        # add a filter model to filter matching items
        self.pFilterModel = QSortFilterProxyModel(self)
        self.pFilterModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.pFilterModel.setSourceModel(self.model())

        # add a completer, which uses the filter model
        self.completer = QCompleter(self.pFilterModel, self)
        # always show all (filtered) completions
        self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.setCompleter(self.completer)

        # connect signals
        self.lineEdit().textEdited.connect(self.pFilterModel.setFilterFixedString)
        self.completer.activated.connect(self.on_completer_activated)

    # on selection of an item from the completer, select the corresponding item from combobox
    def on_completer_activated(self, text):
        if text:
            index = self.findText(text)
            self.setCurrentIndex(index)
            self.activated[str].emit(self.itemText(index))

    # on model change, update the models of the filter and completer as well
    def setModel(self, model):
        super(ExtendedComboBox, self).setModel(model)
        self.pFilterModel.setSourceModel(model)
        self.completer.setModel(self.pFilterModel)

    # on model column change, update the model column of the filter and completer as well
    def setModelColumn(self, column):
        self.completer.setCompletionColumn(column)
        self.pFilterModel.setFilterKeyColumn(column)
        super(ExtendedComboBox, self).setModelColumn(column)


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QStringListModel

    app = QApplication(sys.argv)

    # string_list = ['hola muchachos', 'adios amigos', 'hello world', 'good bye']

    string_list = {'asia': {'Afghanistan': 'UTC+04:30', 'Armenia': 'UTC+04:00', 'Azerbaijan': 'UTC+04:00', 'Bahrain': 'UTC+03:00', 'Bangladesh': 'UTC+06:00', 'Bhutan': 'UTC+06:00', 'Brunei': 'UTC+08:00', 'Burma (Myanmar)': 'UTC+06:30', 'Cambodia': 'UTC+07:00', 'China': 'UTC+08:00', 'Cyprus': 'UTC+03:00', 'Gaza Strip': 'UTC+03:00', 'Georgia': 'UTC+04:00', 'Hong Kong': 'UTC+08:00', 'India': 'UTC+05:30', 'Indonesia - Jakarta': 'UTC+07:00', 'Indonesia - Makassar': 'UTC+08:00', 'Indonesia - Pontianak': 'UTC+07:00', 'Iran': 'UTC+04:30', 'Iraq': 'UTC+03:00', 'Israel': 'UTC+03:00', 'Japan': 'UTC+09:00', 'Jordan': 'UTC+03:00', 'Kazakhstan - Almaty': 'UTC+06:00', 'Kazakhstan - Aqtobe': 'UTC+05:00', 'Kazakhstan - Astana': 'UTC+06:00', 'Kuwait': 'UTC+03:00', 'Kyrgyzstan': 'UTC+06:00', 'Laos': 'UTC+07:00', 'Lebanon': 'UTC+03:00', 'Malaysia': 'UTC+08:00', 'Mongolia - Central and Eastern': 'UTC+09:00', 'Mongolia - Western': 'UTC+08:00', 'Myanmar': 'UTC+06:30', 'Nepal': 'UTC+05:45', 'North Korea': 'UTC+08:30', 'Oman': 'UTC+04:00', 'Pakistan': 'UTC+05:00', 'Philippines': 'UTC+08:00', 'Qatar': 'UTC+03:00', 'Russia - Moscow': 'UTC+03:00', 'Saudi Arabia': 'UTC+03:00', 'Singapore': 'UTC+08:00', 'South Korea': 'UTC+09:00', 'Sri Lanka': 'UTC+05:30', 'Syria': 'UTC+03:00', 'Taiwan': 'UTC+08:00', 'Tajikistan': 'UTC+05:00', 'Thailand': 'UTC+07:00', 'Timor-Leste': 'UTC+09:00', 'Turkey': 'UTC+03:00', 'Turkmenistan': 'UTC+05:00', 'United Arab Emirates': 'UTC+04:00', 'Uzbekistan': 'UTC+05:00', 'Vietnam': 'UTC+07:00', 'West Bank': 'UTC+03:00', 'Yemen': 'UTC+03:00'}, 'africa': {'Algeria': 'UTC+01:00', 'Angola': 'UTC+01:00', 'Benin': 'UTC+01:00', 'Botswana': 'UTC+02:00', 'Burkina Faso': 'UTC+00:00', 'Burundi': 'UTC+02:00', 'Cameroon': 'UTC+01:00', 'Cape Verde': 'UTC-01:00', 'Central African Republic': 'UTC+01:00', 'Chad': 'UTC+01:00', 'Comoros': 'UTC+03:00', 'Congo Republic of': 'UTC+01:00', "Cote d'Ivoire": 'UTC+00:00', 'Congo (DRC) Kinshasa': 'UTC+01:00', 'Congo (DRC Lubumbashi)': 'UTC+02:00', 'Djibouti': 'UTC+03:00', 'Egypt': 'UTC+02:00', 'Equatorial Guinea': 'UTC+01:00', 'Eritrea': 'UTC+03:00', 'Ethiopia': 'UTC+03:00', 'Gabon': 'UTC+01:00', 'Gambia': 'UTC+00:00', 'Ghana': 'UTC+00:00', 'Guinea': 'UTC+00:00', 'Guinea Bissau': 'UTC+00:00', 'Kenya': 'UTC+03:00', 'Lesotho': 'UTC+02:00', 'Liberia': 'UTC+00:00', 'Libya': 'UTC+02:00', 'Madagascar': 'UTC+03:00', 'Malawi': 'UTC+02:00', 'Mali': 'UTC+00:00', 'Mauritania': 'UTC+00:00', 'Mauritius': 'UTC+04:00', 'Mayotte': 'UTC+03:00', 'Morocco': 'UTC+01:00', 'Mozambique': 'UTC+02:00', 'Namibia': 'UTC+02:00', 'Niger': 'UTC+01:00', 'Nigeria': 'UTC+01:00', 'Reunion': 'UTC+04:00', 'Rwanda': 'UTC+02:00', 'Saint Helena': 'UTC+00:00', 'Sao Tome e Principe': 'UTC+00:00', 'Senegal': 'UTC+00:00', 'Seychelles': 'UTC+04:00', 'Sierra Leone': 'UTC+00:00', 'Somalia': 'UTC+03:00', 'South Africa': 'UTC+02:00', 'South Sudan': 'UTC+03:00', 'Sudan': 'UTC+03:00', 'Swaziland': 'UTC+02:00', 'Tanzania': 'UTC+03:00', 'Togo': 'UTC+00:00', 'Tunisia': 'UTC+01:00', 'Uganda': 'UTC+03:00', 'Western Sahara': 'UTC+01:00', 'Zambia': 'UTC+02:00', 'Zimbabwe': 'UTC+02:00'}, 'antarctica': {'Rothera Research Station': 'UTC-03:00', 'Showa Station': 'UTC+03:00', 'Mawson Station': 'UTC+05:00', 'Vostok Station': 'UTC+06:00', 'Davis': 'UTC+07:00', 'Casey': 'UTC+08:00', 'Dumont dUrville': 'UTC+10:00', 'New Zealand': 'UTC+12:00'}, 'australia': {'Australian Capital Territory': 'UTC+10:00', 'Victoria': 'UTC+10:00', 'Tasmania': 'UTC+10:00', 'New South Wales': 'UTC+10:00', 'Queensland': 'UTC+10:00', 'Northern Territory': 'UTC+09:30', 'Western Australia': 'UTC+08:00', 'Western Australia (Eucla)': 'UTC+08:45', 'South Australia': 'UTC+09:30'}, 'europe': {'Albania': 'UTC+02:00', 'Andorra': 'UTC+02:00', 'Austria': 'UTC+02:00', 'Belarus': 'UTC+03:00', 'Belgium': 'UTC+02:00', 'Bosnia Hercegovina': 'UTC+02:00', 'Bulgaria': 'UTC+03:00', 'Canary Islands': 'UTC+01:00', 'Channel Islands': 'UTC+01:00', 'Croatia': 'UTC+02:00', 'Cyprus': 'UTC+03:00', 'Czech Republic': 'UTC+02:00', 'Denmark': 'UTC+02:00', 'England': 'UTC+01:00', 'Estonia': 'UTC+03:00', 'Faroe Islands': 'UTC+01:00', 'Finland': 'UTC+03:00', 'France': 'UTC+02:00', 'Georgia': 'UTC+04:00', 'Germany': 'UTC+02:00', 'Gibraltar': 'UTC+02:00', 'Greece': 'UTC+03:00', 'Greenland - Nuuk': 'UTC-02:00', 'Hungary': 'UTC+02:00', 'Iceland': 'UTC+00:00', 'Ireland': 'UTC+01:00', 'Isle of Man': 'UTC+01:00', 'Italy': 'UTC+02:00', 'Jersey': 'UTC+01:00', 'Kosovo': 'UTC+02:00', 'Latvia': 'UTC+03:00', 'Liechtenstein': 'UTC+02:00', 'Lithuania': 'UTC+03:00', 'Luxembourg': 'UTC+02:00', 'Macedonia': 'UTC+02:00', 'Malta': 'UTC+02:00', 'Moldova': 'UTC+03:00', 'Monaco': 'UTC+02:00', 'Montenegro': 'UTC+02:00', 'Netherlands': 'UTC+02:00', 'Northern Ireland': 'UTC+01:00', 'Norway': 'UTC+02:00', 'Poland': 'UTC+02:00', 'Portugal': 'UTC+01:00', 'Portugal - Azores': 'UTC+00:00', 'Romania': 'UTC+03:00', 'San Marino': 'UTC+02:00', 'Scotland': 'UTC+01:00', 'Serbia': 'UTC+02:00', 'Slovakia': 'UTC+02:00', 'Slovenia': 'UTC+02:00', 'Spain': 'UTC+02:00', 'Sweden': 'UTC+02:00', 'Switzerland': 'UTC+02:00', 'Turkey': 'UTC+03:00', 'Ukraine': 'UTC+03:00', 'United Kingdom': 'UTC+01:00', 'Vatican City': 'UTC+02:00', 'Wales': 'UTC+01:00'}, 'north america': {'Hawaii-Aleutian': 'UTC-10:00', 'Alaska': 'UTC-09:00', 'Pacific': 'UTC-08:00', 'Mountain': 'UTC-07:00', 'Central': 'UTC-06:00', 'Eastern': 'UTC-05:00', 'Atlantic': 'UTC-04:00', 'Newfoundland': 'UTC-03:30', 'West Greenland': 'UTC-03:00', 'Saint Pierre and Miquelon': 'UTC-03:00', 'East Greenland': 'UTC-01:00'}, 'south america': {'Argentina': 'UTC-03:00', 'Bolivia': 'UTC-04:00', 'Chile': 'UTC-03:00', 'Brazil - Federal District': 'UTC-03:00', 'Brazil - Rio de Janeiro': 'UTC-03:00', 'Brazil -Sao Paulo': 'UTC-03:00', 'Columbia': 'UTC-05:00', 'Easter Island': 'UTC-05:00', 'Ecuador': 'UTC-05:00', 'Falkland Islands': 'UTC-03:00', 'French Guiana': 'UTC-03:00', 'Galapagos Islands': 'UTC-06:00', 'Guyana': 'UTC-04:00', 'Paraguay': 'UTC-04:00', 'Peru': 'UTC-05:00', 'Suriname': 'UTC-03:00', 'Uruguay': 'UTC-03:00', 'Venezuela': 'UTC-04:00'}}

    combo = ExtendedComboBox()

    # either fill the standard model of the combobox
    # combo.addItems(string_list)

    # or use another model
    combo.setModel(QStringListModel(string_list))

    combo.resize(300, 40)
    combo.show()

    sys.exit(app.exec_())
