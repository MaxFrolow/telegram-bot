# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'telegram-bot.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from db_process import DbProcessor
import sys


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        self.area_show = QtWidgets.QTextEdit(Dialog)
        self.area_show.setReadOnly(True)
        self.area_show.setGeometry(QtCore.QRect(20, 20, 261, 141))
        self.area_show.setObjectName("area_show")
        self.button_show = QtWidgets.QPushButton(Dialog)
        self.button_show.setGeometry(QtCore.QRect(310, 40, 79, 25))
        self.button_show.setObjectName("button_show")
        self.button_clean = QtWidgets.QPushButton(Dialog)
        self.button_clean.setGeometry(QtCore.QRect(310, 70, 79, 25))
        self.button_clean.setObjectName("butto_show")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.button_show.setText(_translate("Dialog", "Show"))
        self.button_clean.setText(_translate("Dialog", "Clean"))


class DbApp(QtWidgets.QMainWindow, Ui_Dialog, DbProcessor):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.button_show.clicked.connect(self.show_data)
        self.button_clean.clicked.connect(self.clear_area)


    def show_data(self):
        data = super().get_data()
        self.area_show.setPlainText(data)

    def clear_area(self):
        self.area_show.clear()




def main():
    app = QtWidgets.QApplication(sys.argv)
    window = DbApp()
    window.show()
    app.exec_()

main()