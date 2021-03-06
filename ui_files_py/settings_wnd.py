# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'settings_wnd.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(600, 400)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtWidgets.QTabWidget(Form)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.formLayout = QtWidgets.QFormLayout(self.tab)
        self.formLayout.setObjectName("formLayout")
        self.label_2 = QtWidgets.QLabel(self.tab)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.lesson_price_sb = QtWidgets.QSpinBox(self.tab)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.lesson_price_sb.setFont(font)
        self.lesson_price_sb.setMaximum(10000)
        self.lesson_price_sb.setSingleStep(50)
        self.lesson_price_sb.setObjectName("lesson_price_sb")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lesson_price_sb)
        self.label_4 = QtWidgets.QLabel(self.tab)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.max_non_active_period_sb = QtWidgets.QSpinBox(self.tab)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.max_non_active_period_sb.setFont(font)
        self.max_non_active_period_sb.setMaximum(9999)
        self.max_non_active_period_sb.setObjectName("max_non_active_period_sb")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.max_non_active_period_sb)
        self.label_6 = QtWidgets.QLabel(self.tab)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_6)
        self.abonement_duration_sb = QtWidgets.QSpinBox(self.tab)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.abonement_duration_sb.setFont(font)
        self.abonement_duration_sb.setObjectName("abonement_duration_sb")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.abonement_duration_sb)
        self.label_7 = QtWidgets.QLabel(self.tab)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_7)
        self.org_name_le = QtWidgets.QLineEdit(self.tab)
        self.org_name_le.setObjectName("org_name_le")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.org_name_le)
        self.label_8 = QtWidgets.QLabel(self.tab)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label_8)
        self.org_slogan_le = QtWidgets.QLineEdit(self.tab)
        self.org_slogan_le.setObjectName("org_slogan_le")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.org_slogan_le)
        self.label = QtWidgets.QLabel(self.tab)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.label)
        self.label_5 = QtWidgets.QLabel(self.tab)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.hide_zero_rows_chb = QtWidgets.QCheckBox(self.tab)
        self.hide_zero_rows_chb.setText("")
        self.hide_zero_rows_chb.setObjectName("hide_zero_rows_chb")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.hide_zero_rows_chb)
        self.label_3 = QtWidgets.QLabel(self.tab)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.can_delete_chb = QtWidgets.QCheckBox(self.tab)
        self.can_delete_chb.setText("")
        self.can_delete_chb.setChecked(True)
        self.can_delete_chb.setObjectName("can_delete_chb")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.can_delete_chb)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.sound_label = QtWidgets.QLabel(self.tab)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.sound_label.setFont(font)
        self.sound_label.setText("")
        self.sound_label.setObjectName("sound_label")
        self.horizontalLayout.addWidget(self.sound_label)
        self.select_btn = QtWidgets.QPushButton(self.tab)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.select_btn.setFont(font)
        self.select_btn.setObjectName("select_btn")
        self.horizontalLayout.addWidget(self.select_btn)
        self.standard_btn = QtWidgets.QPushButton(self.tab)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.standard_btn.setFont(font)
        self.standard_btn.setObjectName("standard_btn")
        self.horizontalLayout.addWidget(self.standard_btn)
        self.formLayout.setLayout(5, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.tab_2)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.days_gb = QtWidgets.QGroupBox(self.tab_2)
        self.days_gb.setObjectName("days_gb")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.days_gb)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.fri_rb = QtWidgets.QRadioButton(self.days_gb)
        self.fri_rb.setObjectName("fri_rb")
        self.gridLayout_3.addWidget(self.fri_rb, 4, 0, 1, 1)
        self.mon_rb = QtWidgets.QRadioButton(self.days_gb)
        self.mon_rb.setChecked(True)
        self.mon_rb.setObjectName("mon_rb")
        self.gridLayout_3.addWidget(self.mon_rb, 0, 0, 1, 1)
        self.sat_rb = QtWidgets.QRadioButton(self.days_gb)
        self.sat_rb.setObjectName("sat_rb")
        self.gridLayout_3.addWidget(self.sat_rb, 5, 0, 1, 1)
        self.wed_rb = QtWidgets.QRadioButton(self.days_gb)
        self.wed_rb.setObjectName("wed_rb")
        self.gridLayout_3.addWidget(self.wed_rb, 2, 0, 1, 1)
        self.tue_rb = QtWidgets.QRadioButton(self.days_gb)
        self.tue_rb.setObjectName("tue_rb")
        self.gridLayout_3.addWidget(self.tue_rb, 1, 0, 1, 1)
        self.thu_rb = QtWidgets.QRadioButton(self.days_gb)
        self.thu_rb.setObjectName("thu_rb")
        self.gridLayout_3.addWidget(self.thu_rb, 3, 0, 1, 1)
        self.sun_rb = QtWidgets.QRadioButton(self.days_gb)
        self.sun_rb.setObjectName("sun_rb")
        self.gridLayout_3.addWidget(self.sun_rb, 6, 0, 1, 1)
        self.gridLayout_4.addWidget(self.days_gb, 0, 0, 1, 1)
        self.add_lesson_btn = QtWidgets.QPushButton(self.tab_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.add_lesson_btn.sizePolicy().hasHeightForWidth())
        self.add_lesson_btn.setSizePolicy(sizePolicy)
        self.add_lesson_btn.setMaximumSize(QtCore.QSize(200, 16777215))
        self.add_lesson_btn.setObjectName("add_lesson_btn")
        self.gridLayout_4.addWidget(self.add_lesson_btn, 1, 1, 1, 1)
        self.lessons_table = QtWidgets.QTableWidget(self.tab_2)
        self.lessons_table.setObjectName("lessons_table")
        self.lessons_table.setColumnCount(4)
        self.lessons_table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.lessons_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.lessons_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.lessons_table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.lessons_table.setHorizontalHeaderItem(3, item)
        self.gridLayout_4.addWidget(self.lessons_table, 0, 1, 1, 1)
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tab_3)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.lesson_types_table = QtWidgets.QTableWidget(self.tab_3)
        self.lesson_types_table.setObjectName("lesson_types_table")
        self.lesson_types_table.setColumnCount(5)
        self.lesson_types_table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.lesson_types_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.lesson_types_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.lesson_types_table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.lesson_types_table.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.lesson_types_table.setHorizontalHeaderItem(4, item)
        self.gridLayout_2.addWidget(self.lesson_types_table, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_3, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.save_btn = QtWidgets.QPushButton(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.save_btn.sizePolicy().hasHeightForWidth())
        self.save_btn.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.save_btn.setFont(font)
        self.save_btn.setObjectName("save_btn")
        self.gridLayout.addWidget(self.save_btn, 1, 0, 1, 1)

        self.retranslateUi(Form)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Окно настроек"))
        self.label_2.setText(_translate("Form", "Стоимость занятия"))
        self.label_4.setText(_translate("Form", "Длительность неактивного периода"))
        self.label_6.setText(_translate("Form", "Стандартная длительность абонемента"))
        self.label_7.setText(_translate("Form", "Название организации"))
        self.label_8.setText(_translate("Form", "Девиз"))
        self.label.setText(_translate("Form", "Звук окончания занятия"))
        self.label_5.setText(_translate("Form", "Скрывать нулевые строки в статистике"))
        self.label_3.setText(_translate("Form", "Запрет удалять записи прошлых дней"))
        self.select_btn.setText(_translate("Form", "Выбрать"))
        self.standard_btn.setText(_translate("Form", "По умолчанию"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("Form", "Основные найстройки"))
        self.days_gb.setTitle(_translate("Form", "День недели"))
        self.fri_rb.setText(_translate("Form", "Пятница"))
        self.mon_rb.setText(_translate("Form", "Понедельник"))
        self.sat_rb.setText(_translate("Form", "Суббота"))
        self.wed_rb.setText(_translate("Form", "Среда"))
        self.tue_rb.setText(_translate("Form", "Вторник"))
        self.thu_rb.setText(_translate("Form", "Четверг"))
        self.sun_rb.setText(_translate("Form", "Воскресенье"))
        self.add_lesson_btn.setText(_translate("Form", "Добавить занятие"))
        item = self.lessons_table.horizontalHeaderItem(0)
        item.setText(_translate("Form", "id"))
        item = self.lessons_table.horizontalHeaderItem(1)
        item.setText(_translate("Form", "Тип занятия"))
        item = self.lessons_table.horizontalHeaderItem(2)
        item.setText(_translate("Form", "Время"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("Form", "Расписание"))
        item = self.lesson_types_table.horizontalHeaderItem(0)
        item.setText(_translate("Form", "id"))
        item = self.lesson_types_table.horizontalHeaderItem(1)
        item.setText(_translate("Form", "Тип занятия"))
        item = self.lesson_types_table.horizontalHeaderItem(2)
        item.setText(_translate("Form", "Время занятия"))
        item = self.lesson_types_table.horizontalHeaderItem(3)
        item.setText(_translate("Form", "Цвет занятия"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("Form", "Типы занятий"))
        self.save_btn.setText(_translate("Form", "Сохранить и закрыть"))
