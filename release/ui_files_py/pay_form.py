# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pay_form.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(415, 300)
        self.formLayout = QtWidgets.QFormLayout(Form)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.client_cb = QtWidgets.QComboBox(Form)
        self.client_cb.setObjectName("client_cb")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.client_cb)
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.total_sum_sb = QtWidgets.QSpinBox(Form)
        self.total_sum_sb.setMinimum(0)
        self.total_sum_sb.setMaximum(100000)
        self.total_sum_sb.setDisplayIntegerBase(10)
        self.total_sum_sb.setObjectName("total_sum_sb")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.total_sum_sb)
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.lesson_amount_sb = QtWidgets.QSpinBox(Form)
        self.lesson_amount_sb.setObjectName("lesson_amount_sb")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.lesson_amount_sb)
        self.pay_btn = QtWidgets.QPushButton(Form)
        self.pay_btn.setObjectName("pay_btn")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.pay_btn)
        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.update_duration_cb = QtWidgets.QCheckBox(Form)
        self.update_duration_cb.setText("")
        self.update_duration_cb.setObjectName("update_duration_cb")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.update_duration_cb)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Форма для оплаты"))
        self.label.setText(_translate("Form", "Клиент"))
        self.label_2.setText(_translate("Form", "Внесенная сумма"))
        self.label_3.setText(_translate("Form", "Количество занятий        "))
        self.pay_btn.setText(_translate("Form", "Оплатить"))
        self.label_4.setText(_translate("Form", "Обновить длительность абонемента  "))