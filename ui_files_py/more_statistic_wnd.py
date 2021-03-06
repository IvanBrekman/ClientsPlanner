# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'more_statistic_wnd.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(641, 455)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.exit_btn = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.exit_btn.sizePolicy().hasHeightForWidth())
        self.exit_btn.setSizePolicy(sizePolicy)
        self.exit_btn.setObjectName("exit_btn")
        self.gridLayout.addWidget(self.exit_btn, 2, 0, 1, 1)
        self.data_label = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(20)
        self.data_label.setFont(font)
        self.data_label.setText("")
        self.data_label.setAlignment(QtCore.Qt.AlignCenter)
        self.data_label.setObjectName("data_label")
        self.gridLayout.addWidget(self.data_label, 0, 0, 1, 1)
        self.tabWidget = QtWidgets.QTabWidget(Form)
        self.tabWidget.setObjectName("tabWidget")
        self.attendance_tab = QtWidgets.QWidget()
        self.attendance_tab.setObjectName("attendance_tab")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.attendance_tab)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.attendance_table = QtWidgets.QTableWidget(self.attendance_tab)
        self.attendance_table.setObjectName("attendance_table")
        self.attendance_table.setColumnCount(4)
        self.attendance_table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.attendance_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.attendance_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.attendance_table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.attendance_table.setHorizontalHeaderItem(3, item)
        self.gridLayout_2.addWidget(self.attendance_table, 0, 0, 1, 1)
        self.tabWidget.addTab(self.attendance_tab, "")
        self.payments_tab = QtWidgets.QWidget()
        self.payments_tab.setObjectName("payments_tab")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.payments_tab)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.payments_table = QtWidgets.QTableWidget(self.payments_tab)
        self.payments_table.setObjectName("payments_table")
        self.payments_table.setColumnCount(5)
        self.payments_table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.payments_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.payments_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.payments_table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.payments_table.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.payments_table.setHorizontalHeaderItem(4, item)
        self.gridLayout_3.addWidget(self.payments_table, 0, 0, 1, 1)
        self.tabWidget.addTab(self.payments_tab, "")
        self.gridLayout.addWidget(self.tabWidget, 1, 0, 1, 1)

        self.retranslateUi(Form)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Подробная статистика"))
        self.exit_btn.setText(_translate("Form", "Закрыть"))
        item = self.attendance_table.horizontalHeaderItem(0)
        item.setText(_translate("Form", "Клиент"))
        item = self.attendance_table.horizontalHeaderItem(1)
        item.setText(_translate("Form", "Дата"))
        item = self.attendance_table.horizontalHeaderItem(2)
        item.setText(_translate("Form", "Время"))
        item = self.attendance_table.horizontalHeaderItem(3)
        item.setText(_translate("Form", "Тип занятия"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.attendance_tab), _translate("Form", "Посещения"))
        item = self.payments_table.horizontalHeaderItem(0)
        item.setText(_translate("Form", "Клиент"))
        item = self.payments_table.horizontalHeaderItem(1)
        item.setText(_translate("Form", "Дата"))
        item = self.payments_table.horizontalHeaderItem(2)
        item.setText(_translate("Form", "Время"))
        item = self.payments_table.horizontalHeaderItem(3)
        item.setText(_translate("Form", "Сумма оплаты"))
        item = self.payments_table.horizontalHeaderItem(4)
        item.setText(_translate("Form", "Количество занятий"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.payments_tab), _translate("Form", "Оплаты"))
