import sys
import datetime as dt

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtWidgets import QCalendarWidget, QTableWidget, QPushButton, QCheckBox
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView, QMessageBox, QColorDialog

from PyQt5.QtCore import QDate, QTime
from PyQt5.QtGui import QColor

from ui_files_py import more_statistic_wnd, pay_form, \
    add_income_client_wnd, about_wnd, main_window, client_info_wnd, change_client_wnd, settings_wnd

from check_correct_input import convert_number, convert_name, check_correct_time
from update_data import update_data_in_new_day, update_month_report
from database_requests import *

MY_DB = "clients.db"
MONTHS = {1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель', 5: 'Май', 6: 'Июнь',
          7: 'Июль', 8: 'Август', 9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'}
DAYS = {'Понедельник': 1, 'Вторник': 2, 'Среда': 3, 'Четверг': 4, 'Пятница': 5, 'Суббота': 6,
        'Воскресенье': 7}
CONSTANTS = {}

need_show_mes = True
can_delete_previous_history = False
lesson_am = 0

red = QColor(255, 0, 0)
light_red = QColor('#FA8072')
light_green = QColor('#90FF77')
light_yellow = QColor('#FFFFE0')


class AddLessonWindow(QWidget, add_income_client_wnd.Ui_Form):
    def __init__(self, parent, table: str, date: (QDate, int), time_intervals: list):
        super().__init__()
        self.initUI()

        self.parent = parent
        self.table = table
        self.date = date
        self.all_time_intervals = time_intervals

    def initUI(self):
        self.setupUi(self)
        self.setWindowTitle('Добавить занятие')

        self.client_label.hide()
        self.client_cb.hide()

        self.items = [res[0] for res in get_data_from_db(MY_DB, 'lesson_types', 'name')]
        self.lesson_type_cb.addItems(self.items)

        cur_hour = dt.datetime.now().hour
        end_hours, end_min = calculate_time(cur_hour, 0)

        self.start_lesson_time_te.setTime(QTime(cur_hour, 0))
        self.end_lesson_time_te.setTime(QTime(end_hours, end_min))

        self.message = QMessageBox()
        self.message.setText('Занятие успешно добавлено!')

        self.error_message = QMessageBox()

        self.add_btn.clicked.connect(self.add_lesson)
        self.start_lesson_time_te.timeChanged.connect(self.update_end_time)

    def add_lesson(self):
        if isinstance(self.date, QDate):
            date = f"'{'.'.join(map(str, (self.date.day(), self.date.month(), self.date.year())))}'"
        else:
            date = str(self.date)

        start_time = self.start_lesson_time_te.time()
        start_time_str = f'{start_time.hour():02d}:{start_time.minute():02d}'

        end_time = self.end_lesson_time_te.time()
        end_time_str = f'{end_time.hour():02d}:{end_time.minute():02d}'

        check_time = check_correct_time(start_time, end_time, self.all_time_intervals)
        print(check_time)
        if check_time is not True:
            self.error_message.setText(check_time)
            self.error_message.show()
            return

        self.all_time_intervals.append([start_time, end_time])
        time = f"'{start_time_str}-{end_time_str}'"

        lesson_type_id = str(get_data_from_db(MY_DB, 'lesson_types', 'id',
                                              {'name': [self.lesson_type_cb.currentText()]})[0][0])
        add_data_to_db(MY_DB, self.table, ('date', 'time', 'lesson_type_id'),
                       (date, time, lesson_type_id))

        self.message.show()

        self.parent.load_lessons_table()

    def update_end_time(self):
        """ Обновляет время конца занятия, при изменении времени начала """

        time = self.start_lesson_time_te.time()
        cur_hour, cur_min = time.hour(), time.minute()

        end_hours, end_min = calculate_time(cur_hour, cur_min)
        self.end_lesson_time_te.setTime(QTime(end_hours, end_min))


class AddIncomeClientWindow(QWidget, add_income_client_wnd.Ui_Form):
    def __init__(self, parent, calendar: QCalendarWidget):
        super().__init__()
        self.initUI()

        self.parent = parent
        self.calendar = calendar

    def initUI(self):
        self.setupUi(self)

        self.items = [res[0] for res in get_data_from_db(MY_DB, 'clients', 'name')]
        self.client_cb.addItems(self.items)

        self.items = [res[0] for res in get_data_from_db(MY_DB, 'lesson_types', 'name')]
        self.lesson_type_cb.addItems(self.items)

        cur_hour = dt.datetime.now().hour
        end_hours, end_min = calculate_time(cur_hour, 0)

        self.error_message = QMessageBox()

        self.start_lesson_time_te.setTime(QTime(cur_hour, 0))
        self.end_lesson_time_te.setTime(QTime(end_hours, end_min))

        self.message = QMessageBox()
        self.message.setText('Клиент успешно добавлен!')

        self.add_btn.clicked.connect(self.add_income_client)
        self.start_lesson_time_te.timeChanged.connect(self.update_end_time)

    def add_income_client(self):
        date = self.calendar.selectedDate()
        date = f"'{'.'.join(map(str, (date.day(), date.month(), date.year())))}'"

        start_time = self.start_lesson_time_te.time()
        start_time_str = f'{start_time.hour():02d}:{start_time.minute():02d}'

        end_time = self.end_lesson_time_te.time()
        end_time_str = f'{end_time.hour():02d}:{end_time.minute():02d}'

        time = f"'{start_time_str}-{end_time_str}'"

        check_time = check_correct_time(start_time, end_time, [])
        print(check_time)
        if check_time is not True:
            self.error_message.setText(check_time)
            self.error_message.show()
            return

        lesson_type_id = str(get_data_from_db(MY_DB, 'lesson_types', 'id',
                                              {'name': [self.lesson_type_cb.currentText()]})[0][0])
        client_id = str(get_data_from_db(MY_DB, 'clients', 'id',
                                         {'name': [self.client_cb.currentText()]})[0][0])
        add_data_to_db(MY_DB, 'clients_attendance', ('date', 'time', 'lesson_type_id', 'client_id'),
                       (date, time, lesson_type_id, client_id))
        month, year = date[1:-1].split('.')[1:]
        update_month_report(month, year)

        self.parent.load_month_report_table()
        self.parent.load_income_table()

        self.message.show()

    def update_end_time(self):
        """ Обновляет время конца занятия, при изменении времени начала """

        time = self.start_lesson_time_te.time()
        cur_hour, cur_min = time.hour(), time.minute()

        end_hours, end_min = calculate_time(cur_hour, cur_min)
        self.end_lesson_time_te.setTime(QTime(end_hours, end_min))


class ChangeClientInfoWindow(QWidget, change_client_wnd.Ui_Form):
    def __init__(self, parent, info=None, is_new=False):
        super().__init__()

        self.parent = parent
        self.info = info
        self.is_new = is_new
        self.initUI()

    def initUI(self):
        self.setupUi(self)

        self.message = QMessageBox()

        if not self.info:
            self.client_label.hide()
            self.client_cb.hide()

            self.save_changes_btn.setText('Добавить')

            today = dt.date.today()
            self.reg_date_de.setDate(QDate(today.year, today.month, today.day))
        else:
            self.items = [res[0] for res in get_data_from_db(MY_DB, 'clients', 'name')]

            self.client_cb.addItems(self.items)
            self.change_client(False)

        self.client_cb.currentTextChanged.connect(self.change_client)
        self.save_changes_btn.clicked.connect(self.save_new_info)

    def change_client(self, is_change_item=True):
        """ Обновление информации при смене клиента """

        if is_change_item:
            info = get_data_from_db(MY_DB, 'clients', '*',
                                    {'name': [self.client_cb.currentText()]})[0]
        else:
            info = get_data_from_db(MY_DB, 'clients', '*',
                                    {'name': [self.info[0]], 'phone': [self.info[1]]})[0]

        self.client_id = info[0]
        self.client_cb.setCurrentIndex(self.items.index(info[1]))
        self.name_edit.setText(info[1])
        self.phone_edit.setText(info[2])
        self.reg_date_de.setDate(QDate(*map(int, info[3].split('.')[::-1])))
        self.birth_date_de.setDate(QDate(*map(int, info[4].split('.')[::-1])))
        self.lessons_amount_sb.setValue(info[5])
        self.duration_sb.setValue(info[6])

    def save_new_info(self):
        name = f"'{convert_name(self.name_edit.text())}'"
        phone = f"'{convert_number(self.phone_edit.text())}'"
        reg_date = f"'{self.reg_date_de.date().day()}.{self.reg_date_de.date().month()}." \
                   f"{self.reg_date_de.date().year()}'"
        birth_date = f"'{self.birth_date_de.date().day()}.{self.birth_date_de.date().month()}." \
                     f"{self.birth_date_de.date().year()}'"
        les_amount, dur = f"'{self.lessons_amount_sb.text()}'", f"'{self.duration_sb.text()}'"

        error = []
        if name[1:].strip().startswith("Неверный"):
            error.append(name)
        elif phone[1] != '+':
            error.append(phone)

        if error:
            self.message.setText('\n'.join(error))
            self.message.show()
            return

        cl = ('name', 'phone', 'start_date', 'birth_date',
              'lessons_amount', 'duration', 'is_active', 'non_active_days')
        values = (name, phone, reg_date, birth_date, les_amount, dur, '1', '0')

        if self.is_new:
            add_data_to_db(MY_DB, 'clients', cl, values)
        else:
            update_data_in_db(MY_DB, 'clients', dict(zip(cl[:-2], values[:-2])),
                              {'id': self.client_id})

        self.parent.load_client_table()
        self.destroy()


class ClientInfoWindow(QWidget, client_info_wnd.Ui_Form):
    def __init__(self, client_name):
        super().__init__()

        self.client_name = client_name
        self.initUI()

    def initUI(self):
        self.setupUi(self)

        self.load_table()

        self.client_name_label.setText(self.client_name)

        self.client_info_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.client_info_table.horizontalHeader().resizeSections(QHeaderView.ResizeToContents)

        self.date_filter_de.dateChanged.connect(self.update_table)
        self.exit_btn.clicked.connect(self.exit)

    def load_table(self, attendance=None, payments=None):
        if attendance is None and payments is None:
            client_id = str(get_data_from_db(MY_DB, 'clients', 'id',
                                             {'name': [self.client_name]})[0][0])
            attendance = get_data_from_db(MY_DB, 'clients_attendance', '*',
                                          {'client_id': [client_id]})
            payments = get_data_from_db(MY_DB, 'payments_table', '*', {'client_id': [client_id]})

        if not (attendance or payments):
            self.client_info_table.setRowCount(0)
            return
        for i, at in enumerate(attendance):
            attendance[i] = list(at)
            lesson_type = get_data_from_db(MY_DB, 'lesson_types', 'name', {'id': [str(at[3])]})[0][0]
            attendance[i][3] = lesson_type

        info = [el[1:-1] + [''] for el in attendance] + [list(el)[1:-1] for el in payments]
        info.sort(key=lambda x: dt.datetime(*map(int, x[0].split('.')[::-1]),
                                            *map(int, x[1].split('-')[0].split(':'))))
        print(*info, sep='\n')

        self.client_info_table.setRowCount(0)
        for i in range(len(info)):
            self.client_info_table.setRowCount(self.client_info_table.rowCount() + 1)
            self.client_info_table.setItem(i, 0,
                                           QTableWidgetItem('Оплата' if info[i][-1] else 'Занятие'))
            for j in range(len(info[0])):
                self.client_info_table.setItem(i, j + 1, QTableWidgetItem(str(info[i][j])))
            paintRow(self.client_info_table, i, light_green if bool(info[i][-1]) else light_yellow)

    def update_table(self):
        """ Обновление таблицы в соответствии с новой датой """

        client_id = str(get_data_from_db(MY_DB, 'clients', 'id', {'name': [self.client_name]})[0][0])
        print(client_id)
        date = self.date_filter_de.date()

        atd = get_data_from_db(MY_DB, 'clients_attendance', '*', {'client_id': [client_id]})
        pmt = get_data_from_db(MY_DB, 'payments_table', '*', {'client_id': [client_id]})

        attendance = list(filter(lambda x: dt.date(*map(int, x[1].split('.')[::-1])) >= date, atd))
        payments = list(filter(lambda x: dt.date(*map(int, x[1].split('.')[::-1])) >= date, pmt))

        if len(attendance + payments) != self.client_info_table.rowCount():
            print('update_table')
            print(*(attendance + payments))
            self.load_table(attendance, payments)



    def exit(self):
        self.destroy()


class PayWindow(QWidget, pay_form.Ui_Form):
    def __init__(self, parent, calendar):
        super().__init__()
        self.initUI()

        self.parent = parent
        self.calendar = calendar

    def initUI(self):
        self.setupUi(self)

        self.items = [res[0] for res in get_data_from_db(MY_DB, 'clients', 'name')]
        self.client_cb.addItems(self.items)

        self.message = QMessageBox()
        self.message.setText('Оплата произведена успешно')

        self.error_message = QMessageBox()
        self.error_message.setText('Сумма оплаты или количество оплаченных занятий равны 0')

        self.total_sum_sb.valueChanged.connect(self.update_lesson_amount)
        self.pay_btn.clicked.connect(self.take_pay)

    def update_lesson_amount(self, value):
        self.lesson_amount_sb.setValue(value // int(CONSTANTS["lesson_price"]))

    def take_pay(self):
        money = self.total_sum_sb.text()
        lesson_amount = self.lesson_amount_sb.text()

        if not (money != '0' and lesson_amount != '0'):
            self.error_message.show()
            return

        date = dt.date.today()  # self.calendar.selectedDate() ????????????
        date = f"'{'.'.join(map(str, (date.day, date.month, date.year)))}'"
        time = f"'{dt.datetime.now().hour:02d}:{dt.datetime.now().minute:02d}'"

        need_update = self.update_duration_cb.isChecked()
        client_id = str(get_data_from_db(MY_DB, 'clients', 'id',
                                         {'name': [self.client_cb.currentText()]})[0][0])
        values = {'lessons_amount': f'lessons_amount + {lesson_amount}',
                  'duration': CONSTANTS['abonement_duration'] if need_update else 'duration'}

        add_data_to_db(MY_DB, 'payments_table',
                       ('date', 'time', 'client_id', 'pay_sum', 'lesson_amount'),
                       (date, time, client_id, money, lesson_amount))
        update_data_in_db(MY_DB, 'clients', values, {'id': client_id})

        month, year = date[1:-1].split('.')[1:]
        update_month_report(month, year)

        self.parent.load_month_report_table()
        self.parent.load_client_table()

        self.message.show()


class MoreStatisticWindow(QWidget, more_statistic_wnd.Ui_Form):
    def __init__(self, month_number: int, year: str):
        super().__init__()

        self.month = month_number
        self.year = year
        self.initUI()

    def initUI(self):
        self.setupUi(self)

        self.data_label.setText(f'{MONTHS[self.month]} {self.year}')

        self.load_table(self.attendance_table, 'clients_attendance')
        self.load_table(self.payments_table, 'payments_table')

        self.attendance_table.horizontalHeader().resizeSections(QHeaderView.ResizeToContents)
        self.attendance_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        self.payments_table.horizontalHeader().resizeSections(QHeaderView.ResizeToContents)
        self.payments_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        self.exit_btn.clicked.connect(self.exit)

    def load_table(self, table: QTableWidget, db_table: str):
        cond = {'date': f'%.{self.month}.{self.year}'}
        info = [list(el) for el in get_data_from_db(MY_DB, db_table, '*', conditions_like=cond)]
        for i in range(len(info)):
            info[i][0] = get_data_from_db(MY_DB, 'clients', 'name', {'id': [str(info[i][-1])]})[0][0]
            if table == self.attendance_table:
                info[i][-2] = get_data_from_db(MY_DB, 'lesson_types', 'name',
                                               {'id': [str(info[i][-2])]})[0][0]
        info.sort(key=lambda el: dt.datetime(*map(int, el[1].split('.')[::-1]),
                                             *map(int, el[2].split('-')[0].split(':'))))
        print(info)
        table.setRowCount(0)
        for i in range(len(info)):
            table.setRowCount(table.rowCount() + 1)
            for j in range(len(info[0]) - 1):
                table.setItem(i, j, QTableWidgetItem(str(info[i][j])))

    def exit(self):
        self.destroy()


class SettingsWindow(QWidget, settings_wnd.Ui_Form):
    def __init__(self, parent):
        super().__init__()

        self.parent = parent
        self.load_lessons_table = self.load_page2

        self.initUI()

    def initUI(self):
        self.setupUi(self)

        self.days = [self.mon_rb, self.tue_rb, self.wed_rb, self.thu_rb, self.fri_rb, self.sat_rb,
                     self.sun_rb]
        for rb in self.days:
            rb.toggled.connect(lambda args: self.load_page2(args))

        self.lessons_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.lessons_table.setColumnHidden(0, True)

        self.load_page1()
        self.load_page2()
        self.load_page3()

        self.add_lesson_btn.clicked.connect(self.show_add_lesson_wnd)
        self.save_btn.clicked.connect(self.saveNewSettings)

    def load_page1(self):
        self.params = [self.lesson_price_sb, self.lesson_duration_sb, self.max_non_active_period_sb,
                       self.abonement_duration_sb]
        for i, (key, value) in enumerate(list(CONSTANTS.items())[:-2]):
            self.params[i].setValue(int(CONSTANTS[key]))

        self.hide_zero_rows_chb.setCheckState(int(CONSTANTS['hide_zero_rows_in_statistic']) * 2)
        self.can_delete_chb.setCheckState(int(not can_delete_previous_history) * 2)

    def load_page2(self, is_checked_rb=None):
        if is_checked_rb:
            return

        self.del_lesson_btn = []
        self.all_intervals = []
        self.lessons_table.setRowCount(0)

        date = str(DAYS[self.get_selected_day()])
        info = [list(el) for el in get_data_from_db(MY_DB, 'lessons_timetable',
                                                    'id, lesson_type_id, time', {'date': [date]})]
        lessons_type_id = [str(res[1]) for res in info]
        for i, lt_id in enumerate(lessons_type_id):
            type_name = get_data_from_db(MY_DB, 'lesson_types', 'name', {'id': [lt_id]})[0][0]
            info[i][1] = type_name
        info.sort(key=lambda res: dt.time(*map(int, res[2].split('-')[0].split(':'))))

        for i in range(len(info)):
            self.lessons_table.setRowCount(self.lessons_table.rowCount() + 1)
            for j in range(len(info[0])):
                if j == 2:
                    t_func = lambda time: dt.time(*map(int, time.split(':')))
                    self.all_intervals.append(list(map(t_func, info[i][j].split('-'))))
                self.lessons_table.setItem(i, j, QTableWidgetItem(str(info[i][j])))

            btn = QPushButton('-', self)
            btn.clicked.connect(lambda x: self.delete_row(self.lessons_table, self.del_lesson_btn,
                                                          True))
            self.del_lesson_btn.append(btn)
            self.lessons_table.setCellWidget(i, 3, btn)
            self.lessons_table.setItem(i, 3, QTableWidgetItem(""))

            color = get_data_from_db(MY_DB, 'lesson_types', 'color', {'name': [info[i][1]]})[0][0]
            paintRow(self.lessons_table, i, QColor(color))

        self.lessons_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)

    def load_page3(self):
        self.color_btn = []
        self.delete_type_btn = []
        self.lesson_types_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.lesson_types_table.horizontalHeader().resizeSections(QHeaderView.ResizeToContents)
        self.lesson_types_table.setColumnHidden(0, True)
        self.lesson_types_table.setRowCount(1)

        info = get_data_from_db(MY_DB, 'lesson_types', '*')

        for i in range(len(info)):
            self.lesson_types_table.setRowCount(self.lesson_types_table.rowCount() + 1)
            for j in range(len(info[0]) - 1):
                self.lesson_types_table.setItem(i, j, QTableWidgetItem(str(info[i][j])))

            self.add_buttons_in_row(i, info[i][2])

        btn = QPushButton('+', self)
        btn.clicked.connect(self.add_row)
        self.lesson_types_table.setCellWidget(self.lesson_types_table.rowCount() - 1, 3, btn)

    def show_add_lesson_wnd(self):
        self.add_lesson_window = AddLessonWindow(self, 'lessons_timetable',
                                                 DAYS[self.get_selected_day()], self.all_intervals)
        self.add_lesson_window.show()

    def get_selected_day(self):
        for radio_btn in self.days:
            if radio_btn.isChecked():
                return radio_btn.text()
    
    def add_buttons_in_row(self, row, color):
        btn = QPushButton('Выбрать цвет', self)
        btn.setStyleSheet(f'background-color: {color}')
        btn.clicked.connect(self.choose_color)
        self.color_btn.append(btn)
        self.lesson_types_table.setCellWidget(row, 2, btn)
        self.lesson_types_table.setItem(row, 2, QTableWidgetItem(""))

        btn = QPushButton('-', self)
        btn.clicked.connect(lambda x: self.delete_row(self.lesson_types_table, self.delete_type_btn))
        self.delete_type_btn.append(btn)
        self.lesson_types_table.setCellWidget(row, 3, btn)

    def add_row(self):
        global lesson_am
        lesson_am += 1

        self.lesson_types_table.insertRow(rows := self.lesson_types_table.rowCount() - 1)
        self.lesson_types_table.setItem(rows, 0, QTableWidgetItem(str(rows + 1)))
        self.lesson_types_table.setItem(rows, 1, QTableWidgetItem('Занятие' + str(lesson_am)))
        self.add_buttons_in_row(self.lesson_types_table.rowCount() - 2, 'white')

    def choose_color(self):
        color = QColorDialog.getColor(self.sender().palette().button().color())
        if color.isValid():
            self.sender().setStyleSheet(f'background-color: {color.name()}')
            print(color.name())

    def delete_row(self, table: QTableWidget, array_buttons: (list, tuple), need_delete_in_db=False):
        array_buttons.pop(row := array_buttons.index(self.sender()))
        if need_delete_in_db:
            delete_data_from_db(MY_DB, 'lessons_timetable', {'id': table.item(row, 0).text()})
        table.removeRow(row)

    def get_lesson_types_info(self):
        info = []
        table = self.lesson_types_table

        for i in range(self.lesson_types_table.rowCount() - 1):
            info.append([f'"{table.item(i, j).text()}"' for j in range(table.columnCount() - 1)])
            info[i][2] = f'"{self.color_btn[i].palette().button().color().name()}"'

        return info

    def saveNewSettings(self):
        global can_delete_previous_history

        can_delete_previous_history = not self.can_delete_chb.isChecked()

        values = [param.text() for param in self.params] + [int(self.hide_zero_rows_chb.isChecked())]
        for i, value in enumerate(values, 1):
            update_data_in_db(MY_DB, 'settings', {'value': value}, {'id': i})

        update_constants()

        delete_data_from_db(MY_DB, 'lesson_types', {})
        for row in self.get_lesson_types_info():
            add_data_to_db(MY_DB, 'lesson_types', ('id', 'name', 'color'), row)

        self.destroy()

        self.parent.update_planner_tab_tables()
        self.parent.load_client_table()
        self.parent.load_month_report_table()


class AboutWindow(QWidget, about_wnd.Ui_Form):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setupUi(self)


class MainWindow(QMainWindow, main_window.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setupUi(self)

        self.ordering_index = None
        self.ordering = False
        self.is_name_filtered = False

        self.message = QMessageBox()

        self.about_action.triggered.connect(self.show_about_wnd)
        self.preferences_action.triggered.connect(self.show_settings_wnd)
        self.about_wnd = AboutWindow()

        years = get_data_from_db(MY_DB, 'month_reports', 'year', is_distinct=True)
        self.year_cb.addItems(sorted(map(str, [year[0] for year in years]), reverse=True))

        self.load_month_report_table()
        self.load_lessons_table()
        self.load_income_table()
        self.load_client_table()

        self.lessons_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.lessons_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.lessons_table.setColumnHidden(0, True)

        self.incoming_clients_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.incoming_clients_table.setColumnHidden(1, True)

        self.client_base_table.horizontalHeader().resizeSections(QHeaderView.ResizeToContents)
        self.client_base_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.client_base_table.setColumnHidden(0, True)

        self.search_line.textChanged.connect(self.search_by_name)
        self.year_cb.currentTextChanged.connect(self.update_year_statistic)
        self.client_base_table.horizontalHeader().sectionClicked.connect(self.sort_table)
        self.calendar.clicked.connect(self.update_planner_tab_tables)
        self.add_lesson_btn.clicked.connect(self.show_add_lesson_wnd)
        self.add_client_btn.clicked.connect(self.show_add_income_client_wnd)
        self.add_client_db_btn.clicked.connect(self.show_add_client_table_wnd)
        self.pushButton.clicked.connect(self.fill_lessons_automatically)
        self.pay_btn.clicked.connect(self.show_pay_form)
        self.change_client_btn.clicked.connect(self.show_change_client_table_wnd)

    def show_change_client_table_wnd(self):
        try:
            name = self.full_names[self.client_base_table.currentItem().row()]
            phone = self.client_base_table.item(self.client_base_table.currentItem().row(), 2).text()
            self.change_client_wnd = ChangeClientInfoWindow(self, (name, phone))
            self.change_client_wnd.show()
        except AttributeError:
            print(self.client_base_table.currentItem())
            self.message.setText('Ячейка не выбрана')
            self.message.show()

    def show_add_client_table_wnd(self):
        self.change_client_wnd = ChangeClientInfoWindow(self, is_new=True)
        self.change_client_wnd.show()

    def show_add_income_client_wnd(self):
        self.add_income_client_wnd = AddIncomeClientWindow(self, self.calendar)
        self.add_income_client_wnd.show()

    def show_add_lesson_wnd(self):
        self.add_lesson_window = AddLessonWindow(self, 'lessons', self.calendar.selectedDate(),
                                                 self.lessons_time_intervals)
        self.add_lesson_window.show()

    def show_pay_form(self):
        self.pay_form_wnd = PayWindow(self, self.calendar)
        self.pay_form_wnd.show()

    def show_settings_wnd(self):
        self.settings_wnd = SettingsWindow(self)
        self.settings_wnd.show()

    def show_about_wnd(self):
        self.about_wnd.show()

    def show_client_info(self):
        full_name = self.full_names[self.clients_buttons.index(self.sender())]
        self.client_info_wnd = ClientInfoWindow(full_name)
        self.client_info_wnd.show()

    def show_more_statistic(self):
        row = self.more_statistic_buttons.index(self.sender())
        month, year = row + 1, self.year_cb.currentText()

        self.more_statistic_wnd = MoreStatisticWindow(month, year)
        self.more_statistic_wnd.show()

    def load_client_table(self, info=None):
        global need_show_mes

        self.client_activate_checkboxes = []
        self.clients_buttons = []
        self.full_names = []

        if info is None:
            info = get_data_from_db(MY_DB, 'clients', '*')

        print(info)
        self.client_base_table.setRowCount(0)

        for i in range(len(info)):
            self.client_base_table.setRowCount(self.client_base_table.rowCount() + 1)
            for j in range(len(info[0]) - 1):
                if j == 1:
                    btn = QPushButton(' '.join(info[i][j].split()[:2]), self)
                    btn.clicked.connect(self.show_client_info)
                    self.clients_buttons.append(btn)
                    self.full_names.append(info[i][j])

                    self.client_base_table.setCellWidget(i, 1, btn)
                elif j == len(info[0]) - 2:
                    checkbox = QCheckBox()

                    checkbox.setChecked(bool(info[i][j]))
                    checkbox.setText(str(info[i][j + 1]) if not info[i][j] else '')
                    if info[i][j + 1] >= int(CONSTANTS['max_non_active_period']) and need_show_mes:
                        need_show_mes = False

                        text = f'Пользователь {self.full_names[i]} неактивен больше указанного срока'
                        self.message.setText(text)
                        self.message.show()

                    checkbox.stateChanged.connect(self.update_client_activity)

                    self.client_activate_checkboxes.append(checkbox)
                    self.client_base_table.setCellWidget(i, j, checkbox)
                    self.client_base_table.setItem(i, j, QTableWidgetItem(""))

                    remain = int(CONSTANTS["max_non_active_period"]) - info[i][j + 1]
                    if remain <= 2:
                        self.paint_column(i, j, remain)
                else:
                    if j == 4:
                        item = calculate_age(dt.date(*map(int, info[i][j].split('.')[::-1])))
                    else:
                        item = str(info[i][j])
                    self.client_base_table.setItem(i, j, QTableWidgetItem(item))

                    if j in (5, 6) and info[i][j] <= 2:
                        self.paint_column(i, j, info[i][j])

    def load_income_table(self):
        self.clients_delete_buttons = []

        date = self.calendar.selectedDate()
        date = '.'.join(map(str, (date.day(), date.month(), date.year())))
        id__time__client_id = [res for res in
                               get_data_from_db(MY_DB, 'clients_attendance',
                                                'id, time, client_id', {'date': [date]})]
        table_id = [str(el[0]) for el in id__time__client_id]
        times = [str(el[1]) for el in id__time__client_id]
        clients_id = [str(el[2]) for el in id__time__client_id]
        print(table_id, clients_id)
        info = []
        for i, c_id in enumerate(clients_id):
            name = get_data_from_db(MY_DB, 'clients', 'name', {'id': [c_id]})[0][0]
            info.append((table_id[i], times[i], name))
        print(info)
        print('-' * 40)
        self.incoming_clients_table.setRowCount(0)

        for i in range(len(info)):
            self.incoming_clients_table.setRowCount(self.incoming_clients_table.rowCount() + 1)
            for j in range(len(info[0]) + 1):
                if j == 0:
                    btn = QPushButton('-', self)
                    btn.clicked.connect(self.delete_row_from_incoming_clients_table)
                    if (not can_delete_previous_history and
                            dt.date(*map(int, date.split('.')[::-1])) < dt.date.today()):
                        btn.setEnabled(False)
                    self.clients_delete_buttons.append(btn)

                    self.incoming_clients_table.setCellWidget(i, j, btn)
                else:
                    self.incoming_clients_table.setItem(i, j, QTableWidgetItem(str(info[i][j - 1])))

    def load_lessons_table(self):
        self.lessons_delete_buttons = []
        self.lessons_time_intervals = []

        date = self.calendar.selectedDate()
        date = '.'.join(map(str, (date.day(), date.month(), date.year())))

        info = [list(res) for res in get_data_from_db(MY_DB, 'lessons', 'id, lesson_type_id, time',
                                                      {'date': [date]})]

        lessons_type_id = [str(res[1]) for res in info]
        for i, lt_id in enumerate(lessons_type_id):
            type_name = get_data_from_db(MY_DB, 'lesson_types', 'name', {'id': [lt_id]})[0][0]
            info[i][1] = type_name
        info.sort(key=lambda res: dt.time(*map(int, res[2].split('-')[0].split(':'))))
        print(info)
        print('-' * 40)
        self.lessons_table.setRowCount(0)

        for i in range(len(info)):
            self.lessons_table.setRowCount(self.lessons_table.rowCount() + 1)
            for j in range(len(info[0]) + 1):
                if j == len(info[0]):
                    btn = QPushButton('-', self)
                    btn.clicked.connect(self.delete_row_from_lessons_table)
                    if (not can_delete_previous_history and
                            dt.date(*map(int, date.split('.')[::-1])) < dt.date.today()):
                        btn.setEnabled(False)
                    self.lessons_delete_buttons.append(btn)

                    self.lessons_table.setCellWidget(i, j, btn)
                    self.lessons_table.setItem(i, j, QTableWidgetItem(""))
                else:
                    if j == 2:
                        t_func = lambda time: dt.time(*map(int, time.split(':')))
                        self.lessons_time_intervals.append(list(map(t_func, info[i][j].split('-'))))
                    self.lessons_table.setItem(i, j, QTableWidgetItem(str(info[i][j])))

            color = get_data_from_db(MY_DB, 'lesson_types', 'color', {'name': [info[i][1]]})[0][0]
            paintRow(self.lessons_table, i, QColor(color))

    def load_month_report_table(self):
        self.more_statistic_buttons = []

        year = self.year_cb.currentText()
        info = get_data_from_db(MY_DB, 'month_reports', 'month, clients_amount, total_sum',
                                {'year': [year]}, ordering={'month': 0})
        info += [(i, 0, 0) for i in range(1, 12 + 1) if i not in (el[0] for el in info)]
        info.sort(key=lambda x: x[0])
        print(info)
        total_sum = 0

        for i in range(12):
            for j in range(1, len(info[0])):
                data = str(info[i][j]) if j == 1 else beauty_number(info[i][j])
                self.month_reports_table.setItem(i, j - 1, QTableWidgetItem(data))
            total_sum += info[i][2]

            if int(CONSTANTS['hide_zero_rows_in_statistic']) and list(info[i][1:]) == [0, 0]:
                self.month_reports_table.hideRow(i)
            else:
                self.month_reports_table.showRow(i)

            btn = QPushButton('+', self)
            btn.clicked.connect(self.show_more_statistic)
            self.more_statistic_buttons.append(btn)

            self.month_reports_table.setCellWidget(i, 2, btn)
            self.month_reports_table.setItem(i, 2, QTableWidgetItem(""))

        self.outcome_lbl.setText(beauty_number(total_sum) + chr(8381))

    def delete_row_from_incoming_clients_table(self):
        delete_row = self.clients_delete_buttons.index(self.sender())
        deleted_id = self.incoming_clients_table.item(delete_row, 1).text()
        date = get_data_from_db(MY_DB, 'clients_attendance', 'date', {'id': [deleted_id]})[0][0]
        print(delete_row, deleted_id)

        self.clients_delete_buttons.pop(self.clients_delete_buttons.index(self.sender()))
        self.incoming_clients_table.removeRow(delete_row)
        delete_data_from_db(MY_DB, 'clients_attendance', {'id': deleted_id})

        month, year = date.split('.')[1:]
        update_month_report(month, year)
        self.load_month_report_table()

    def delete_row_from_lessons_table(self):
        delete_row = self.lessons_delete_buttons.index(self.sender())
        deleted_id = self.lessons_table.item(delete_row, 0).text()
        print(delete_row, deleted_id)

        self.lessons_time_intervals.pop(delete_row)
        self.lessons_delete_buttons.pop(self.lessons_delete_buttons.index(self.sender()))
        self.lessons_table.removeRow(delete_row)
        delete_data_from_db(MY_DB, 'lessons', {'id': deleted_id})
    
    def fill_lessons_automatically(self):
        date = self.calendar.selectedDate()
        day = date.dayOfWeek()
        date = f"'{'.'.join(map(str, (date.day(), date.month(), date.year())))}'"
        
        delete_data_from_db(MY_DB, 'lessons', {'date': date[1:-1]})

        for lesson in get_data_from_db(MY_DB, 'lessons_timetable', '*', {'date': [str(day)]}):
            lesson = list(map(lambda el: f'"{el}"', lesson[1:]))
            lesson[0] = date
            add_data_to_db(MY_DB, 'lessons', ('date', 'time', 'lesson_type_id'), lesson)

        self.load_lessons_table()

    def sort_table(self, index):
        if index == 2:
            return

        if self.ordering_index != index:
            self.ordering = False

        if self.is_name_filtered:
            info = get_data_from_db(MY_DB, 'clients', '*',
                                    conditions_like={'name': '%' + self.search_line.text() + '%'})
        else:
            info = get_data_from_db(MY_DB, 'clients', '*')

        if index in (3, 4):
            key_func = lambda x: dt.date(*map(int, reversed(x[index].split('.'))))
        else:
            key_func = lambda x: x[index]
        rev = self.ordering if index != 4 else not self.ordering
        sorted_info = sorted(info, key=key_func, reverse=rev)

        self.ordering = not self.ordering
        self.ordering_index = index

        self.load_client_table(sorted_info)

    def search_by_name(self):
        request = self.search_line.text()

        if len(request) > 1:
            info = get_data_from_db(MY_DB, 'clients', '*', conditions_like={'name': f'%{request}%'})
            self.is_name_filtered = True
        else:
            info = get_data_from_db(MY_DB, 'clients', '*')
            self.is_name_filtered = False

        self.load_client_table(info)

    def update_client_activity(self):
        """ Обновляет состояние активности клиента в таблице клиентов """

        if self.sender().isChecked():
            text = f'Вы действительно хотите вернуть активность этого клиента?'
            valid = QMessageBox.question(self, '', text, QMessageBox.Yes, QMessageBox.No)

            if valid == QMessageBox.No:
                self.load_client_table()
                return

        my_row = self.client_activate_checkboxes.index(self.sender())
        client_id = self.client_base_table.item(my_row, 0).text()
        update_data_in_db(MY_DB, 'clients',
                          {'is_active': int(self.sender().isChecked()), 'non_active_days': '0'},
                          {'id': client_id})
        self.load_client_table()

    def update_planner_tab_tables(self):
        self.load_lessons_table()
        self.load_income_table()

    def update_year_statistic(self):
        self.load_month_report_table()

    def paint_column(self, row, col, val):
        self.client_base_table.item(row, col).setBackground(red if val <= 0 else light_red)

    def closeEvent(self, event) -> None:
        """ Обновление даты последней активности при закрытии приложения """

        date = dt.date.today()
        date = f'"{date.day}.{date.month}.{date.year}"'
        update_data_in_db(MY_DB, 'settings', {'value': date}, {'param': 'last_activity_date'})


def paintRow(table: QTableWidget, row: int, color: QColor):
    for col in range(table.columnCount()):
        table.item(row, col).setBackground(color)


def calculate_age(born: dt.date) -> str:
    today = dt.date.today()
    return str(today.year - born.year - ((today.month, today.day) < (born.month, born.day)))


def calculate_time(cur_hour: int, cur_min: int):
    """ Подсчет время конца действия, учитывая начальное время и длительность действия """

    end_sec = (dt.timedelta(hours=cur_hour, minutes=cur_min) +
               dt.timedelta(minutes=int(CONSTANTS["lesson_duration"]))).seconds
    end_hours = end_sec // 3600
    end_min = (end_sec // 60) % 60

    return end_hours, end_min


def beauty_number(number: (int, str)) -> str:
    """ Красиво форматирует денежную сумму """

    beauty_num = ''

    for i, digit in enumerate(str(number)[::-1]):
        beauty_num = digit + beauty_num
        if i % 3 == 2:
            beauty_num = ' ' + beauty_num

    return beauty_num.strip()


def update_constants():
    global CONSTANTS
    CONSTANTS = dict(get_data_from_db(MY_DB, 'settings', 'param, value'))


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Обновление информации
    update_constants()
    update_data_in_new_day()
    update_month_report(str(dt.date.today().month), str(dt.date.today().year))
    #

    wnd = MainWindow()
    wnd.show()

    sys.excepthook = except_hook
    sys.exit(app.exec())
