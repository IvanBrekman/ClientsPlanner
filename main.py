import sys
import pyglet
import datetime as dt

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtWidgets import QCalendarWidget, QTableWidget, QPushButton, QCheckBox, QLineEdit
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView, QMessageBox, QColorDialog, QFileDialog

from PyQt5.QtCore import QDate, QTimer, QSize, QRegExp, Qt
from PyQt5.QtGui import QColor, QIcon, QRegExpValidator, QIntValidator

from ui_files_py import more_statistic_wnd, pay_form, add_income_client_wnd, about_wnd, main_window,\
    client_info_wnd, change_client_wnd, settings_wnd, lesson_timer_wnd, select_date_wnd

from check_correct_input import convert_number, convert_name, check_correct_time
from update_data import update_data_in_new_day, update_month_report
from database_requests import *

# Объявление констант
MY_DB = "clients.db"
MONTHS = {1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель', 5: 'Май', 6: 'Июнь',
          7: 'Июль', 8: 'Август', 9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'}
DAYS = {'Понедельник': 1, 'Вторник': 2, 'Среда': 3, 'Четверг': 4, 'Пятница': 5,
        'Суббота': 6, 'Воскресенье': 7}
DEFAULT_DATE = QDate(2020, 11, 1)
MAX_SOUND_DURATION_SECONDS = 30
CONSTANTS = {}

need_show_mes = True
can_delete_previous_history = False
lesson_am = play_time = 0
delete_char = chr(10_005)
more_char = chr(128_269)

red = QColor('#FF6666')
light_red = QColor('#FF9933')
light_green = QColor('#90FF77')
light_yellow = QColor('#FFFFE0')
light_blue = QColor('#CCCCFF')
transparent = QColor('#000000')
#


class AddForm(QWidget, add_income_client_wnd.Ui_Form):
    """ Родительский класс, описывающий поведение при добавлении занятия или клиента """

    def __init__(self):
        super().__init__()

    def initUI(self):
        self.setupUi(self)

        # получение возможных значений для comboBox
        self.items = [res[0] for res in get_data_from_db(MY_DB, 'clients', 'name')]
        self.client_cb.addItems(self.items)

        self.items = [res[0] for res in get_data_from_db(MY_DB, 'lesson_types', 'name')]
        self.lesson_type_cb.addItems(self.items)
        # Получение базовой длительности занятия #
        self.min = get_data_from_db(MY_DB, 'lesson_types', 'duration',
                                    {'name': [self.items[0]]})[0][0]
        #

        # Заполнение базового времени начала и конца занятия
        cur_hour = dt.datetime.now().hour
        end_hours, end_min = calculate_time(cur_hour, 0, self.min)

        self.start_lesson_time_le.setText(dt.time(cur_hour, 0).strftime('%H:%M'))
        self.end_lesson_time_le.setText(dt.time(end_hours, end_min).strftime('%H:%M'))
        #

        self.message = QMessageBox()
        self.message.setText('Занятие успешно добавлено!')

        self.error_message = QMessageBox()

        # Подключение различных триггеров на элементы управления
        self.add_btn.clicked.connect(self.add_note)
        self.start_lesson_time_le.editingFinished.connect(self.update_end_time)
        self.start_lesson_time_le.textChanged.connect(self.check_time)
        self.end_lesson_time_le.textChanged.connect(self.check_time)
        self.lesson_type_cb.currentIndexChanged.connect(self.change_end_time)
        #

    def check_time(self):
        """ Метод проверки корректности введенного времени """

        first_part, second_part = self.sender().text().split(':')  # Получение введенного времени
        if len(first_part) == 2:
            first_part = str(min(int(first_part), 23)).rjust(2, '0')  # Добавление лидирующих 0
        if len(second_part) == 2:
            second_part = str(min(int(second_part), 59)).rjust(2, '0')  # Добавление лидирующих 0
        time = first_part + ':' + second_part

        # Установка позиции курсора после обновления времени
        pos = self.sender().cursorPosition()
        self.sender().setText(time)
        self.sender().setCursorPosition(pos)
        #

    def change_end_time(self):
        """ Метод устанавливает время конца занятия, основываясь на его длительности """

        self.min = get_data_from_db(MY_DB, 'lesson_types', 'duration',
                                    {'name': [self.lesson_type_cb.currentText()]})[0][0]
        self.update_end_time()

    def update_end_time(self):
        """ Метод обновляет время конца занятия, при изменении времени начала """

        cur_hour, cur_min = map(lambda y: int(y.rjust(2, '0')),
                                self.start_lesson_time_le.text().split(':'))
        end_hours, end_min = calculate_time(cur_hour, cur_min, self.min)
        self.start_lesson_time_le.setText(dt.time(cur_hour, cur_min).strftime('%H:%M'))
        self.end_lesson_time_le.setText(dt.time(end_hours, end_min).strftime('%H:%M'))


class AddLessonWindow(AddForm):
    """ Класс-наслденик для добавления нового занятия в расписание """

    def __init__(self, parent, table: str, date: (QDate, int), time_intervals: list):
        super().__init__()
        self.initUI()

        self.parent = parent
        self.table = table
        self.date = date
        self.all_time_intervals = time_intervals

    def initUI(self):
        super().initUI()
        self.setWindowTitle('Добавить занятие')

        # Скрывает ненужные для данного окна виджеты выбора клиента
        self.client_cb.hide()
        self.client_label.hide()
        #

    def add_note(self):
        """ Метод добавляет новую запись в базу данных и отображает изменения """

        # Приводит время к строковому представлению
        if isinstance(self.date, QDate):
            date = f"'{self.date.toString('yyyy.MM.dd')}'"
        else:
            date = str(self.date)
        #

        # Приводит время к формату хранения времени в бд
        start_time = dt.time(*map(int, self.start_lesson_time_le.text().split(':')))
        start_time_str = f'{start_time.hour:02d}:{start_time.minute:02d}'

        end_time = dt.time(*map(int, self.end_lesson_time_le.text().split(':')))
        end_time_str = f'{end_time.hour:02d}:{end_time.minute:02d}'
        #

        # Проверка возможности добавления записи в указанный промежуток времени
        check_time = check_correct_time(start_time, end_time, self.all_time_intervals)
        print(check_time)
        if check_time is not True:  # Уведомление пользователя, если указанное время уже занято
            self.error_message.setText(check_time)
            self.error_message.show()
            return
        #

        # Запоминаем новый занятый промежуток времени для дальнейших проверок #
        self.all_time_intervals.append([start_time, end_time])
        time = f"'{start_time_str}-{end_time_str}'"

        # Добавляем новую запись в базу данных
        lesson_type_id = str(get_data_from_db(MY_DB, 'lesson_types', 'id',
                                              {'name': [self.lesson_type_cb.currentText()]})[0][0])
        add_data_to_db(MY_DB, self.table, ('date', 'time', 'lesson_type_id'),
                       (date, time, lesson_type_id))
        #

        self.message.show()  # Показываем уведомление об успешном выполнении действия

        self.parent.load_lessons_table()  # Обновляем таблицу занятий


class AddIncomeClientWindow(AddForm):
    """ Класс-наслденик для добавления клиента, посетившего занятие """

    def __init__(self, parent, calendar: QCalendarWidget):
        super().__init__()
        self.initUI()

        self.parent = parent
        self.calendar = calendar

    def initUI(self):
        super().initUI()
        self.message.setText('Клиент успешно добавлен')

    def add_note(self):
        """ Метод добавляет новую запись в базу данных и отображает изменения """

        # Приводит время к формату хранения в бд
        date = f"'{self.calendar.selectedDate().toString('yyyy.MM.dd')}'"

        start_time = dt.time(*map(int, self.start_lesson_time_le.text().split(':')))
        start_time_str = f'{start_time.hour:02d}:{start_time.minute:02d}'

        end_time = dt.time(*map(int, self.end_lesson_time_le.text().split(':')))
        end_time_str = f'{end_time.hour:02d}:{end_time.minute:02d}'

        time = f"'{start_time_str}-{end_time_str}'"
        #

        # Проверка корректности указанного промежутка времени (время начала < времени конца)
        check_time = check_correct_time(start_time, end_time, [])
        print(check_time)
        if check_time is not True:  # Уведомление пользователя в случае некорректного времени
            self.error_message.setText(check_time)
            self.error_message.show()
            return
        #

        # Добавление записи в базу данных
        lesson_type_id = str(get_data_from_db(MY_DB, 'lesson_types', 'id',
                                              {'name': [self.lesson_type_cb.currentText()]})[0][0])
        client_id = str(get_data_from_db(MY_DB, 'clients', 'id',
                                         {'name': [self.client_cb.currentText()]})[0][0])
        add_data_to_db(MY_DB, 'clients_attendance', ('date', 'time', 'lesson_type_id', 'client_id'),
                       (date, time, lesson_type_id, client_id))
        year, month = date[1:-1].split('.')[:2]
        update_month_report(month, year)
        #

        # Обновление таблиц
        self.parent.load_month_report_table()
        self.parent.load_income_table()
        #

        self.message.show()  # Показываем уведомление об успешном выполнении действия


class ChangeClientInfoWindow(QWidget, change_client_wnd.Ui_Form):
    """ Класс для изменения или добавления клиента """

    def __init__(self, parent, info=None, is_new=False):
        super().__init__()

        self.parent = parent
        self.info = info
        self.is_new = is_new
        self.initUI()

    def initUI(self):
        self.setupUi(self)

        self.message = QMessageBox()

        # Устанавливаем валидатор на номер телефона
        reg = QRegExp("\\+?[0-9]{11}")
        validator = QRegExpValidator(reg, self)
        self.phone_edit.setValidator(validator)
        #

        # Корректирование внешнего вида окна в зависимости от типа работы (добавление/редактирование)
        if not self.info:  # Добавление
            # Сокрытие ненужных виджетов
            self.client_label.hide()
            self.client_cb.hide()
            #

            self.save_changes_btn.setText('Добавить')

            day = dt.date.today()  # Устанавливаем дату регистрации на сегодня
            self.reg_date_le.setText(QDate(day.year, day.month, day.day).toString('yyyy.MM.dd'))
        else:  # Редактирование
            self.items = [res[0] for res in get_data_from_db(MY_DB, 'clients', 'name')]

            # Добавление возможных клиентов в comboBox
            self.client_cb.addItems(self.items)
            self.change_client(False)

        # Подключение различных триггеров на элементы управления
        self.client_cb.currentTextChanged.connect(self.change_client)
        self.reg_date_le.textChanged.connect(self.check_date)
        self.birth_date_le.textChanged.connect(self.check_date)
        self.select_reg_date_btn.clicked.connect(self.choose_date)
        self.select_born_date_btn.clicked.connect(self.choose_date)
        self.save_changes_btn.clicked.connect(self.save_new_info)
        #

    def choose_date(self):
        """ Метод показывает окно для выбора даты """

        # Получение текущей даты регистрации
        par = self.reg_date_le if self.sender() == self.select_reg_date_btn else self.birth_date_le
        values = par.text()
        date = QDate(*map(int, values.split('.'))) if len(values) == 10 else QDate.currentDate()
        #

        # Вызов окна выбора даты
        self.choose_date_wnd = ChooseDateWindow(par, date)
        self.choose_date_wnd.show()
        #

    def check_date(self):
        """ Метод проверяет корректность введенной даты """

        # Корректировка даты
        first_part, second_part, third_part = self.sender().text().split('.')
        if len(first_part) == 4:
            first_part = str(min(int(first_part), 2350))
        if len(second_part) == 2:
            second_part = str(min(int(second_part), 12)).rjust(2, '0')
        if len(third_part) == 2:
            third_part = str(min(int(third_part), 31)).rjust(2, '0')
        #

        date = first_part + '.' + second_part + '.' + third_part

        # Установка позиции курсора
        pos = self.sender().cursorPosition()
        self.sender().setText(date)
        self.sender().setCursorPosition(pos)
        #

    def change_client(self, is_change_item=True):
        """ Обновление информации при смене клиента """

        # Получение информации из бд
        if is_change_item:
            info = get_data_from_db(MY_DB, 'clients', '*',
                                    {'name': [self.client_cb.currentText()]})[0]
        else:
            info = get_data_from_db(MY_DB, 'clients', '*',
                                    {'name': [self.info[0]], 'phone': [self.info[1]]})[0]
        #

        # Заполнение виджетов информацией
        self.client_id = info[0]
        self.client_cb.setCurrentIndex(self.items.index(info[1]))
        self.name_edit.setText(info[1])
        self.phone_edit.setText(info[2])
        self.reg_date_le.setText(QDate(*map(int, info[3].split('.'))).toString('yyyy.MM.dd'))
        self.birth_date_le.setText(QDate(*map(int, info[4].split('.'))).toString('yyyy.MM.dd'))
        self.lessons_amount_sb.setValue(info[5])
        self.duration_sb.setValue(info[6])
        #

    def save_new_info(self):
        """ Сохранение измененной информации """

        # Приведение данных к форматц хранения в бд
        name = f"'{convert_name(self.name_edit.text())}'"
        phone = f"'{convert_number(self.phone_edit.text())}'"
        reg_date, birth_date = f"'{self.reg_date_le.text()}'", f"'{self.birth_date_le.text()}'"
        les_amount, dur = f"'{self.lessons_amount_sb.text()}'", f"'{self.duration_sb.text()}'"
        #

        # Проверка данных на корректность
        error = []
        if name[1:].strip().startswith("Неверный"):
            error.append(name)
        if phone[1] != '+':
            error.append(phone)
        if len(reg_date) != 12 or QDate(*map(int, reg_date[1:-1].split('.'))).year() == 0:
            error.append('Неверная дата регистрации')
        if len(birth_date) != 12 or QDate(*map(int, birth_date[1:-1].split('.'))).year() == 0:
            error.append('Неверная дата рождения')

        if error:  # Уведомление пользователя в случае ошибки
            self.message.setText('\n'.join(error))
            self.message.show()
            return
        #

        # Сохранние информации в базу данных
        print()
        cl = ('name', 'phone', 'start_date', 'birth_date',
              'lessons_amount', 'duration', 'is_active', 'non_active_days')
        values = (name, phone, reg_date, birth_date, les_amount, dur, '1', '0')

        if self.is_new:
            add_data_to_db(MY_DB, 'clients', cl, values)
        else:
            update_data_in_db(MY_DB, 'clients', dict(zip(cl[:-2], values[:-2])),
                              {'id': self.client_id})
        #

        self.parent.load_client_table()  # Обновление таблицы клиентов
        self.parent.update_planner_tab_tables()
        self.destroy()


class ChooseDateWindow(QWidget, select_date_wnd.Ui_Form):
    """ Класс для отображения виджета по выбору даты """

    def __init__(self, parent_widget, date: QDate, slot=None):
        super().__init__()

        self.date = date
        self.slot = slot
        self.parent_widget = parent_widget

        self.initUI()

    def initUI(self):
        self.setupUi(self)
        self.calendar.setSelectedDate(self.date)
        self.select_btn.clicked.connect(self.save_data)

    def save_data(self):
        """ Метод сохраняет выбранную дату в родительском виджете """

        self.parent_widget.setText(self.calendar.selectedDate().toString('yyyy.MM.dd'))
        if self.slot is not None:
            self.slot()
        self.destroy()


class ClientInfoWindow(QWidget, client_info_wnd.Ui_Form):
    """ Класс для отображения более подробной информации о клиенте """

    def __init__(self, parent, client_name):
        super().__init__()

        self.parent = parent
        self.client_name = client_name
        self.initUI()

    def initUI(self):
        self.setupUi(self)

        self.load_table()

        self.client_name_label.setText(self.client_name)

        self.client_info_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.client_info_table.horizontalHeader().resizeSections(QHeaderView.ResizeToContents)

        # Подключение различных триггеров на элементы управления
        self.date_filter_le.editingFinished.connect(self.update_table)
        self.date_filter_le.textChanged.connect(self.check_date)
        self.select_btn.clicked.connect(self.choose_date)
        self.exit_btn.clicked.connect(self.exit)
        #

    def load_table(self, attendance=None, payments=None):
        """
        Метод загружает и отображает данные в таблице
        :param attendance: Информация о посещаемости
        :param payments: Информация об оплатах
        """

        # Загрузка данных из бд, если нет информации о посещаемости и об оплатах
        if attendance is None and payments is None:
            self.cl_id = str(get_data_from_db(MY_DB, 'clients', 'id',
                                              {'name': [self.client_name]})[0][0])
            attendance = get_data_from_db(MY_DB, 'clients_attendance', '*',
                                          {'client_id': [self.cl_id]})
            payments = get_data_from_db(MY_DB, 'payments_table', '*', {'client_id': [self.cl_id]})
        #

        if not (attendance or payments):  # Если информации нет, то очищаем таблицу
            self.client_info_table.setRowCount(0)
            return

        # Заполнение таблицы
        # Преобразование информации
        for i, at in enumerate(attendance):
            attendance[i] = list(at)
            lesson_type = get_data_from_db(MY_DB, 'lesson_types', 'name', {'id': [str(at[3])]})[0][0]
            attendance[i][3] = lesson_type

        info = [el[1:-1] + [''] for el in attendance] + [list(el)[1:-1] for el in payments]
        info.sort(key=lambda y: dt.datetime(*map(int, y[0].split('.')),
                                            *map(int, y[1].split('-')[0].split(':'))))
        print(*info, sep='\n')
        #

        self.delete_btn = []
        self.client_info_table.setRowCount(0)
        # Создание строк в таблице #
        for i in range(len(info)):
            j = 0
            self.client_info_table.setRowCount(self.client_info_table.rowCount() + 1)
            self.client_info_table.setItem(i, 0,
                                           QTableWidgetItem('Оплата' if info[i][-1] else 'Занятие'))
            for j in range(len(info[i]) + 1):
                item = str(info[i][j]) if j < len(info[i]) else ""
                self.client_info_table.setItem(i, j + 1, QTableWidgetItem(item))
                self.client_info_table.item(i, j + 1).setFlags(Qt.ItemIsEditable)
                self.client_info_table.item(i, j + 1).setForeground(QColor('black'))

            btn = QPushButton(delete_char, self)
            btn.clicked.connect(self.delete_note)
            self.delete_btn.append(btn)
            self.client_info_table.setCellWidget(i, j + 1, btn)

            # Устанавливает цвет в зависимости от типа записи (оплата/занятие)
            paintRow(self.client_info_table, i, light_green if bool(info[i][-1]) else light_yellow)
        #

    def update_table(self):
        """ Обновление таблицы в соответствии с новой датой """

        try:
            date = QDate(*map(int, self.date_filter_le.text().split('.')))  # Получение даты
            if date.year() == 0:
                raise ValueError
        except ValueError:  # В случае ошибки устанавливает дату на базовое значение
            date = DEFAULT_DATE
            self.date_filter_le.setText(DEFAULT_DATE.strftime('%Y.%m.%d'))
        print(date)

        # Обновление информации в соответсвие с новой датой
        atd = get_data_from_db(MY_DB, 'clients_attendance', '*', {'client_id': [self.cl_id]})
        pmt = get_data_from_db(MY_DB, 'payments_table', '*', {'client_id': [self.cl_id]})

        attendance = list(filter(lambda y: dt.date(*map(int, y[1].split('.'))) >= date, atd))
        payments = list(filter(lambda y: dt.date(*map(int, y[1].split('.'))) >= date, pmt))
        #

        # Если количество записей изменилось, то загружаем таблицу заново
        if len(attendance + payments) != self.client_info_table.rowCount():
            print('update_table')
            print(*(attendance + payments))
            self.load_table(attendance, payments)
        #

    def choose_date(self):
        """ Метод отображает окно для выбора даты """

        values = self.date_filter_le.text()
        date = QDate(*map(int, values.split('.'))) if len(values) == 10 else QDate.currentDate()

        self.choose_date_wnd = ChooseDateWindow(self.date_filter_le, date, self.update_table)
        self.choose_date_wnd.show()

    def check_date(self):
        """ Метод проверяет корректность введенной даты """

        # Корректировка даты
        first_part, second_part, third_part = self.sender().text().split('.')
        if len(first_part) == 4:
            first_part = str(min(int(first_part), 2350))
        if len(second_part) == 2:
            second_part = str(min(int(second_part), 12)).rjust(2, '0')
        if len(third_part) == 2:
            third_part = str(min(int(third_part), 31)).rjust(2, '0')

        date = first_part + '.' + second_part + '.' + third_part
        #

        # Установка позиции курсора
        pos = self.sender().cursorPosition()
        self.sender().setText(date)
        self.sender().setCursorPosition(pos)
        #

    def delete_note(self):
        """ Метод удалет строку из таблицы """

        row = self.delete_btn.index(self.sender())
        get_item = lambda col: self.client_info_table.item(row, col).text()

        # Обновление информации в таблицах в зависимости от удаленной строки (оплата/занятие)
        if get_item(0) == 'Оплата':
            table = 'payments_table'
            columns = ('date', 'time', 'pay_sum', 'lesson_amount')
            update_data_in_db(MY_DB, 'clients', {'lessons_amount': f'lessons_amount -{get_item(4)}'},
                              {'id': self.cl_id})
        else:
            table = 'clients_attendance'
            columns = ('date', 'time')
            val = 1 if dt.date(*map(int, get_item(1).split('.'))) < dt.datetime.now().date() else 0
            update_data_in_db(MY_DB, 'clients', {'lessons_amount': f'lessons_amount + {val}'},
                              {'id': self.cl_id})
        cond = {columns[i - 1]: [get_item(i)] for i in range(1, 5 if get_item(0) == 'Оплата' else 3)}
        cond['client_id'] = [self.cl_id]
        #

        # Обновление таблиц и бд
        delete_data_from_db(MY_DB, table, cond)
        update_month_report(get_item(1).split('.')[1], get_item(1).split('.')[0])
        self.client_info_table.removeRow(row)
        self.delete_btn.pop(row)

        self.parent.update_year_statistic()
        self.parent.update_planner_tab_tables()
        self.parent.load_client_table()
        #

    def exit(self):
        self.destroy()


class PayWindow(QWidget, pay_form.Ui_Form):
    """ Класс для отображения окна оплаты клиента """

    def __init__(self, parent, calendar):
        super().__init__()

        self.parent = parent
        self.calendar = calendar

        self.initUI()

    def initUI(self):
        self.setupUi(self)

        # Загрузка возможных клиентов в comboBox #
        self.items = [res[0] for res in get_data_from_db(MY_DB, 'clients', 'name')]
        self.client_cb.addItems(self.items)
        try:  # Загрузка информации о выбранном клиенте в таблице клиентов (если строка выбрана)
            item = self.parent.client_base_table.currentItem().row()
            index = self.items.index(self.parent.full_names[item])
            self.client_cb.setCurrentIndex(index)
        except AttributeError:
            pass

        self.message = QMessageBox()
        self.message.setText('Оплата произведена успешно')

        self.error_message = QMessageBox()
        self.error_message.setText('Сумма оплаты или количество оплаченных занятий равны 0')

        self.total_sum_sb.valueChanged.connect(self.update_lesson_amount)
        self.pay_btn.clicked.connect(self.take_pay)

    def update_lesson_amount(self, value):
        """ Метод обновляет количество занятий в зависимости от оплачиваемой суммы """
        self.lesson_amount_sb.setValue(value // int(CONSTANTS["lesson_price"]))

    def take_pay(self):
        """ Метод производит оплату и вносит новые записи в бд """

        money = self.total_sum_sb.text()
        lesson_amount = self.lesson_amount_sb.text()

        if not (money != '0' and lesson_amount != '0'):  # Уведомление при некорректных данных
            self.error_message.show()
            return

        # Подготовка данных для бд
        date = dt.date.today()
        date = f"'{date.strftime('%Y.%m.%d')}'"
        time = f"'{dt.datetime.now().hour:02d}:{dt.datetime.now().minute:02d}'"

        need_update = self.update_duration_cb.isChecked()
        client_id = str(get_data_from_db(MY_DB, 'clients', 'id',
                                         {'name': [self.client_cb.currentText()]})[0][0])
        values = {'lessons_amount': f'lessons_amount + {lesson_amount}',
                  'duration': CONSTANTS['abonement_duration'] if need_update else 'duration'}
        #

        # Сохранение информации в бд и обновление таблиц
        add_data_to_db(MY_DB, 'payments_table',
                       ('date', 'time', 'client_id', 'pay_sum', 'lesson_amount'),
                       (date, time, client_id, money, lesson_amount))
        update_data_in_db(MY_DB, 'clients', values, {'id': client_id})

        year, month = date[1:-1].split('.')[:2]
        update_month_report(month, year)

        self.parent.load_month_report_table()
        self.parent.load_client_table()

        self.message.show()
        self.total_sum_sb.setValue(0)
        self.lesson_amount_sb.setValue(0)
        #


class MoreStatisticWindow(QWidget, more_statistic_wnd.Ui_Form):
    """ Класс для отображения подробной статистики за месяц """

    def __init__(self, month_number: int, year: str):
        super().__init__()

        self.month = str(month_number).rjust(2, '0')
        self.year = year
        self.initUI()

    def initUI(self):
        self.setupUi(self)

        self.data_label.setText(f'{MONTHS[int(self.month)]} {self.year}')

        # Загрузка таблиц и редактирование их внешнего вида
        self.load_table(self.attendance_table, 'clients_attendance')
        self.load_table(self.payments_table, 'payments_table')

        self.attendance_table.horizontalHeader().resizeSections(QHeaderView.ResizeToContents)
        self.attendance_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        self.payments_table.horizontalHeader().resizeSections(QHeaderView.ResizeToContents)
        self.payments_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        self.exit_btn.clicked.connect(self.exit)
        #

    def load_table(self, table: QTableWidget, db_table: str):
        """ Загрузка информации в таблицы """

        # Получение и приведение информации из бд
        cond = {'date': f'{self.year}.{self.month}.%'}
        info = [list(el) for el in get_data_from_db(MY_DB, db_table, '*', conditions_like=cond)]
        for i in range(len(info)):
            info[i][0] = get_data_from_db(MY_DB, 'clients', 'name', {'id': [str(info[i][-1])]})[0][0]
            if table == self.attendance_table:
                info[i][-2] = get_data_from_db(MY_DB, 'lesson_types', 'name',
                                               {'id': [str(info[i][-2])]})[0][0]
        info.sort(key=lambda el: dt.datetime(*map(int, el[1].split('.')),
                                             *map(int, el[2].split('-')[0].split(':'))))
        #

        # Загрузка информации в таблицу
        print(info)
        table.setRowCount(0)
        for i in range(len(info)):
            table.setRowCount(table.rowCount() + 1)
            for j in range(len(info[0]) - 1):
                table.setItem(i, j, QTableWidgetItem(str(info[i][j])))
                table.item(i, j).setFlags(Qt.ItemIsEditable)
                table.item(i, j).setForeground(QColor('black'))
        #

    def exit(self):
        self.destroy()


class SettingsWindow(QWidget, settings_wnd.Ui_Form):
    """ Класс для отображения окна настроек приложения """
    def __init__(self, parent):
        super().__init__()

        self.parent = parent
        self.load_lessons_table = self.load_page2

        self.initUI()

    def initUI(self):
        self.setupUi(self)
        
        # Подключение триггеров к radioButton-ам
        self.days = [self.mon_rb, self.tue_rb, self.wed_rb, self.thu_rb, self.fri_rb, self.sat_rb,
                     self.sun_rb]
        for rb in self.days:
            rb.toggled.connect(lambda args: self.load_page2(args))
        #

        self.lessons_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.lessons_table.setColumnHidden(0, True)
        
        # Загрузка страниц окна настроек
        self.load_page1()
        self.load_page2()
        self.load_page3()
        #
        
        # Подключение различных триггеров на элементы управления
        self.select_btn.clicked.connect(self.select_sound)
        self.standard_btn.clicked.connect(self.set_standard_sound)
        self.add_lesson_btn.clicked.connect(self.show_add_lesson_wnd)
        self.save_btn.clicked.connect(self.saveNewSettings)
        #

    def load_page1(self):
        """ Загрузка первой страницы с базовыми настройками приложения """
        
        # Установка значений из бд для всех spinBox
        self.spin_boxes = [self.lesson_price_sb, self.max_non_active_period_sb,
                           self.abonement_duration_sb]
        for i, (key, value) in enumerate(list(CONSTANTS.items())[:-5]):
            self.spin_boxes[i].setValue(int(value))
        #
        
        # Установка значений из бд для всех lineEdit
        self.line_edits = [self.org_name_le, self.org_slogan_le]
        for i, (key, value) in enumerate(list(CONSTANTS.items())[-5:-3]):
            self.line_edits[i].setText(value)
        self.sound_file = CONSTANTS['sound']
        self.sound_label.setText(self.sound_file.split('/')[-1])
        #
        
        # Установка значений из бд для всех checkbox
        self.hide_zero_rows_chb.setCheckState(int(CONSTANTS['hide_zero_rows_in_statistic']) * 2)
        self.can_delete_chb.setCheckState(int(not can_delete_previous_history) * 2)
        #

    def load_page2(self, is_checked_rb=None):
        """ Загрузка второй страницы с настройками базового расписания на неделе """
        
        if is_checked_rb:  # Если было зафиксировано нажатие чекбокса
            return

        self.del_lesson_btn = []
        self.all_intervals = []
        self.lessons_table.setRowCount(0)

        # Подготовка данных для таблицы
        date = str(DAYS[self.get_selected_day()])
        info = [list(el) for el in get_data_from_db(MY_DB, 'lessons_timetable',
                                                    'id, lesson_type_id, time', {'date': [date]})]
        lessons_type_id = [str(res[1]) for res in info]
        for i, lt_id in enumerate(lessons_type_id):
            type_name = get_data_from_db(MY_DB, 'lesson_types', 'name', {'id': [lt_id]})[0][0]
            info[i][1] = type_name
        info.sort(key=lambda res: dt.time(*map(int, res[2].split('-')[0].split(':'))))
        #

        # Загрузка строк в таблицу
        for i in range(len(info)):
            self.lessons_table.setRowCount(self.lessons_table.rowCount() + 1)
            for j in range(len(info[0])):
                if j == 2:  # Обновление информации о занятости времени
                    t_func = lambda time: dt.time(*map(int, time.split(':')))
                    self.all_intervals.append(list(map(t_func, info[i][j].split('-'))))
                self.lessons_table.setItem(i, j, QTableWidgetItem(str(info[i][j])))
                self.lessons_table.item(i, j).setFlags(Qt.ItemIsEditable)
                self.lessons_table.item(i, j).setForeground(QColor('black'))

            btn = QPushButton(delete_char, self)  # Добавление кнопкм для удаления занятия
            btn.clicked.connect(lambda y: self.delete_row(self.lessons_table, self.del_lesson_btn,
                                                          True))
            self.del_lesson_btn.append(btn)
            self.lessons_table.setCellWidget(i, 3, btn)
            self.lessons_table.setItem(i, 3, QTableWidgetItem(""))

            # Окрашивает строку в цвет занятия из бд
            color = get_data_from_db(MY_DB, 'lesson_types', 'color', {'name': [info[i][1]]})[0][0]
            paintRow(self.lessons_table, i, QColor(color))
            #

        self.lessons_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)

    def load_page3(self):
        """ Загрузка третьей страницы с настройками типов занятий """

        self.color_btn = []
        self.delete_type_btn = []
        self.lesson_types_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.lesson_types_table.horizontalHeader().resizeSections(QHeaderView.ResizeToContents)
        self.lesson_types_table.setColumnHidden(0, True)
        self.lesson_types_table.setRowCount(1)

        # Загрузка всех типов занятий в таблицу
        info = get_data_from_db(MY_DB, 'lesson_types', '*')
        for i in range(len(info)):
            self.lesson_types_table.setRowCount(self.lesson_types_table.rowCount() + 1)
            for j in range(len(info[0]) - 1):
                if j == 2:
                    validator = QIntValidator(0, 180)
                    label = QLineEdit(str(info[i][j]))
                    label.setValidator(validator)

                    self.lesson_types_table.setItem(i, j, QTableWidgetItem(''))
                    self.lesson_types_table.setCellWidget(i, j, label)
                else:
                    self.lesson_types_table.setItem(i, j, QTableWidgetItem(str(info[i][j])))

            self.add_buttons_in_row(i, info[i][3])  # Добавление кнопок в строку

        # Добавление кнопки для добавление нового типа занятия
        btn = QPushButton(self)
        btn.setIcon(QIcon('images/plus.png'))
        btn.setIconSize(QSize(28, 28))
        btn.clicked.connect(self.add_row)
        self.lesson_types_table.setCellWidget(self.lesson_types_table.rowCount() - 1, 4, btn)
        #

    def show_add_lesson_wnd(self):
        """ Метод открывает окно для добавления занятия в расписание """
        self.add_lesson_window = AddLessonWindow(self, 'lessons_timetable',
                                                 DAYS[self.get_selected_day()], self.all_intervals)
        self.add_lesson_window.show()

    def get_selected_day(self):
        """ Метод возвращает текст выбранного radioButton-а """
        for radio_btn in self.days:
            if radio_btn.isChecked():
                return radio_btn.text()

    def get_lesson_types_info(self):
        """ Метод возвращает информацию о типе занятия из таблицы для бд """

        info = []
        table = self.lesson_types_table

        for i in range(self.lesson_types_table.rowCount() - 1):
            info.append([f'"{table.item(i, j).text()}"' for j in range(table.columnCount() - 1)])
            info[i][2] = f'"{table.cellWidget(i, 2).text() or "0"}"'
            info[i][3] = f'"{self.color_btn[i].palette().button().color().name()}"'

        return info

    def add_buttons_in_row(self, row, color):
        """ Метод добавляет кнопки для таблицы расписаний """

        # Кнопка выбора цвета
        btn = QPushButton('Выбрать цвет', self)
        btn.setStyleSheet(f'background-color: {color}')
        btn.clicked.connect(self.choose_color)
        self.color_btn.append(btn)
        self.lesson_types_table.setCellWidget(row, 3, btn)
        self.lesson_types_table.setItem(row, 3, QTableWidgetItem(""))
        #

        # Кнопка удаления занятия
        btn = QPushButton(delete_char, self)
        btn.clicked.connect(lambda y: self.delete_row(self.lesson_types_table, self.delete_type_btn))
        self.delete_type_btn.append(btn)
        self.lesson_types_table.setCellWidget(row, 4, btn)
        #

    def add_row(self):
        """ Метод добавляет строку с новым типом занятия """

        global lesson_am
        lesson_am += 1

        validator = QIntValidator(0, 180)
        label = QLineEdit('0')
        label.setValidator(validator)

        self.lesson_types_table.insertRow(rows := self.lesson_types_table.rowCount() - 1)
        self.lesson_types_table.setItem(rows, 0, QTableWidgetItem(str(rows + 1)))
        self.lesson_types_table.setItem(rows, 1, QTableWidgetItem('Занятие' + str(lesson_am)))
        self.lesson_types_table.setItem(rows, 2, QTableWidgetItem(''))
        self.lesson_types_table.setCellWidget(rows, 2, label)
        self.add_buttons_in_row(self.lesson_types_table.rowCount() - 2, 'white')

    def choose_color(self):
        """ Метод запускает виджет для выбора цвета для типа занятия """

        color = QColorDialog.getColor(self.sender().palette().button().color())
        if color.isValid():
            self.sender().setStyleSheet(f'background-color: {color.name()}')
            print(color.name())

    def select_sound(self):
        """ Метод запускает виджет для выбора звукового файла """

        formats = '*.au *.mp2 *.mp3 *.ogg *.vorbis *.wav *.wma'
        file_name, is_ok = QFileDialog.getOpenFileName(self, 'Выбрать файл', 'sounds',
                                                       f'Звук ({formats})')
        if is_ok:
            self.sound_file = file_name
            self.sound_label.setText(file_name.split('/')[-1])

    def set_standard_sound(self):
        """ Метод устанавливает стандартный звук для окончания занятия """

        self.sound_file = 'sound/end_sound.wav'
        self.sound_label.setText('end_sound.wav')

    def delete_row(self, table: QTableWidget, array_buttons: (list, tuple), need_delete_in_db=False):
        """
        Метод удаляет строку из указанной таблицы
        :param table: Таблица из которой удаляется строка
        :param array_buttons: Массив, из которого удаляется упоминание о кнопках
        :param need_delete_in_db: Флажок, отвечающий за необходимость удаления информации из бд
        """

        array_buttons.pop(row := array_buttons.index(self.sender()))
        if need_delete_in_db:
            delete_data_from_db(MY_DB, 'lessons_timetable', {'id': [table.item(row, 0).text()]})
        table.removeRow(row)

    def saveNewSettings(self):
        """ Метод сохраняет все настройки в базе данных """

        global can_delete_previous_history

        # Обновление базовых настроек
        can_delete_previous_history = not self.can_delete_chb.isChecked()

        values = ([f"'{param.text()}'" for param in self.spin_boxes + self.line_edits] +
                  [f"'{self.sound_file}'", int(self.hide_zero_rows_chb.isChecked())])
        for i, value in enumerate(values, 1):
            update_data_in_db(MY_DB, 'settings', {'value': value}, {'id': i})

        update_constants()
        #

        # Обновление информации о типах занятий
        delete_data_from_db(MY_DB, 'lesson_types', {})
        for row in self.get_lesson_types_info():
            add_data_to_db(MY_DB, 'lesson_types', ('id', 'name', 'duration', 'color'), row)
        ids = [str(res[0]) for res in get_data_from_db(MY_DB, 'lesson_types', 'id')]
        delete_data_from_db(MY_DB, 'lessons', {'lesson_type_id': ids}, True)
        delete_data_from_db(MY_DB, 'lessons_timetable', {'lesson_type_id': ids}, True)
        #

        self.destroy()

        # Обновление информации на интерфейсе и обновление таблиц
        self.parent.setWindowTitle(f'Расписание занятий {CONSTANTS["org_name"]}')
        self.parent.slogan_label.setText(CONSTANTS["org_slogan"])
        self.parent.update_planner_tab_tables()
        self.parent.load_client_table()
        self.parent.load_month_report_table()
        #


class LessonTimeWindow(QWidget, lesson_timer_wnd.Ui_Form):
    """ Класс для отображения окна таймера занятия """

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setupUi(self)

        # Загрузка возможных типов уроков для comboBox
        self.items = [res[0] for res in get_data_from_db(MY_DB, 'lesson_types', 'name')]
        self.lesson_types.addItems(self.items)
        self.lesson_types.currentTextChanged.connect(self.set_time)
        #

        # Установка начальных данных
        self.set_current_type()
        self.set_time()
        self.sound = pyglet.media.load(CONSTANTS['sound'])
        self.pause = True
        #

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.set_new_time)

        self.stop_btn.clicked.connect(self.switch_pause)

    def set_current_type(self):
        """ Загрузка текущего типа занятия, основываясь на данных из сегодняшнего расписания """

        cur_date = dt.datetime.now()

        date = cur_date.strftime('%Y.%m.%d')
        time = dt.time(hour=cur_date.hour, minute=cur_date.minute)

        lessons = get_data_from_db(MY_DB, 'lessons', 'lesson_type_id, time', {'date': [date]})
        lesson_type_index = self.get_suitable_lesson_type(lessons, time)

        # Устанавливает тип текущего занятия (если в настоящее время есть заняти в расписании,
        # иначе 1 занятие из списка доступных
        self.lesson_types.setCurrentIndex(lesson_type_index if lesson_type_index != -1 else 0)

    def set_time(self):
        """ Метод устанавливает длительность таймера в зависимости от длительности занятия """

        minutes = get_data_from_db(MY_DB, 'lesson_types', 'duration',
                                   {'name': [self.lesson_types.currentText()]})[0][0]
        self.time_left = dt.timedelta(minutes=minutes)
        self.time.setText(self.time_left.__str__())

    def set_new_time(self):
        """ Метод изменяет время на таймере """

        # Если время закончилось, то воспроизводит звук и останавливает таймер
        if self.time_left.total_seconds() <= 0:
            self.timer.stop()
            self.stop_btn.setEnabled(False)
            play_sound(self.sound)
            return

        self.time_left -= dt.timedelta(seconds=1)
        self.time.setText(self.time_left.__str__())

    def get_suitable_lesson_type(self, lessons: (list, tuple), time: dt.time):
        """ Получение типа занятия в текущее время из таблицы расписания занятий """

        for l_id, l_time in lessons:
            start, end = map(lambda y: dt.time(*map(int, y.split(':'))), l_time.split('-'))

            if start <= time <= end:
                lesson = get_data_from_db(MY_DB, 'lesson_types', 'name', {'id': [str(l_id)]})[0][0]
                return self.items.index(lesson)

        return -1

    def switch_pause(self):
        """ Метод останавливает/воспроизводит таймер """

        self.pause = not self.pause
        self.lesson_types.setEnabled(self.pause)
        self.stop_btn.setText('Старт' if self.pause else 'Стоп')
        self.timer.stop() if self.pause else self.timer.start()

    def closeEvent(self, a0) -> None:
        self.timer.stop()


class AboutWindow(QWidget, about_wnd.Ui_Form):
    """ Класс для отображения окна "О приложении" """

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setupUi(self)


class MainWindow(QMainWindow, main_window.Ui_MainWindow):
    """ Класс основного окна приложения """

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """ Инициализация пользовательского интерфейса """

        # Установка базовых значений
        self.setupUi(self)
        self.setWindowTitle(f'Расписание занятий {CONSTANTS["org_name"]}')
        self.slogan_label.setText(CONSTANTS["org_slogan"])
        self.slogan_label.setStyleSheet("color: green")

        self.ordering_index = None
        self.ordering = False
        self.is_name_filtered = False
        self.cur_row = -1

        self.message = QMessageBox()

        self.about_action.triggered.connect(self.show_about_wnd)
        self.preferences_action.triggered.connect(self.show_settings_wnd)

        years = get_data_from_db(MY_DB, 'month_reports', 'year', is_distinct=True)
        self.year_cb.addItems(sorted(map(str, [year[0] for year in years]), reverse=True))
        #

        # Загрузка всех таблиц
        self.load_month_report_table()
        self.load_lessons_table()
        self.load_income_table()
        self.load_client_table()
        #

        # Изменение отображения таблиц
        self.lessons_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.lessons_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.lessons_table.setColumnHidden(0, True)

        self.incoming_clients_table.horizontalHeader().\
            setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.incoming_clients_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.incoming_clients_table.setColumnHidden(1, True)

        self.client_base_table.horizontalHeader().resizeSections(QHeaderView.ResizeToContents)
        self.client_base_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.client_base_table.setColumnHidden(0, True)
        #

        # Подключение различных триггеров на элементы управления
        self.search_line.textChanged.connect(self.search_by_name)
        self.year_cb.currentTextChanged.connect(self.update_year_statistic)
        self.client_base_table.horizontalHeader().sectionClicked.connect(self.sort_table)
        self.client_base_table.cellClicked.connect(self.update_current_row)
        self.calendar.clicked.connect(self.update_planner_tab_tables)
        self.start_lesson_btn.clicked.connect(self.show_start_lesson_wnd)
        self.fill_automatically_btn.clicked.connect(self.fill_lessons_automatically)
        self.add_lesson_btn.clicked.connect(self.show_add_lesson_wnd)
        self.add_client_btn.clicked.connect(self.show_add_income_client_wnd)
        self.add_client_db_btn.clicked.connect(self.show_add_client_table_wnd)
        self.pay_btn.clicked.connect(self.show_pay_form)
        self.change_client_btn.clicked.connect(self.show_change_client_table_wnd)
        #

    # Методы для отображения окон интерфейса
    def show_change_client_table_wnd(self):
        if self.cur_row != -1:
            name = self.full_names[self.cur_row[0]]
            phone = self.client_base_table.item(self.cur_row[0], 2).text()
            self.change_client_wnd = ChangeClientInfoWindow(self, (name, phone))
            self.change_client_wnd.show()
        else:
            self.message.setText('Ячейка не выбрана')
            self.message.show()

    def show_add_client_table_wnd(self):
        self.change_client_wnd = ChangeClientInfoWindow(self, is_new=True)
        self.change_client_wnd.show()

    def show_start_lesson_wnd(self):
        self.start_lesson_wnd = LessonTimeWindow()
        self.start_lesson_wnd.show()

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
        self.about_wnd = AboutWindow()
        self.about_wnd.show()

    def show_client_info(self):
        full_name = self.full_names[self.clients_buttons.index(self.sender())]
        self.client_info_wnd = ClientInfoWindow(self, full_name)
        self.client_info_wnd.show()

    def show_more_statistic(self):
        row = self.more_statistic_buttons.index(self.sender())
        month, year = row + 1, self.year_cb.currentText()

        self.more_statistic_wnd = MoreStatisticWindow(month, year)
        self.more_statistic_wnd.show()
    #

    # Методы для загрузки таблиц
    def load_client_table(self, info=None):
        """ Загрузка таблицы клиентов """

        global need_show_mes

        self.client_activate_checkboxes = []
        self.clients_buttons = []
        self.full_names = []

        if info is None:
            info = get_data_from_db(MY_DB, 'clients', '*')

        print(info)
        self.client_base_table.setRowCount(0)

        # Загрузка строк в таблицу
        for i in range(len(info)):
            self.client_base_table.setRowCount(self.client_base_table.rowCount() + 1)
            for j in range(len(info[0]) - 1):
                if j == 1:  # Установка кнопки для подробной информации о клиенте
                    btn = QPushButton(' '.join(info[i][j].split()[:2]), self)
                    btn.clicked.connect(self.show_client_info)
                    self.clients_buttons.append(btn)
                    self.full_names.append(info[i][j])

                    self.client_base_table.setCellWidget(i, 1, btn)
                    self.client_base_table.setItem(i, 1, QTableWidgetItem(""))
                elif j == len(info[0]) - 2:  # Установка checkbox об активности клиента
                    checkbox = QCheckBox()

                    checkbox.setChecked(bool(info[i][j]))
                    checkbox.setText(str(info[i][j + 1]) if not info[i][j] else '')

                    # Если период неактивности превышает норму, уведомляем пользователя
                    if info[i][j + 1] >= int(CONSTANTS['max_non_active_period']) and need_show_mes:
                        need_show_mes = False

                        text = f'Пользователь {self.full_names[i]} неактивен больше указанного срока'
                        self.message.setText(text)
                        self.message.show()

                    checkbox.stateChanged.connect(self.update_client_activity)

                    self.client_activate_checkboxes.append(checkbox)
                    self.client_base_table.setCellWidget(i, j, checkbox)
                    self.client_base_table.setItem(i, j, QTableWidgetItem(""))
                    self.client_base_table.item(i, j).setFlags(Qt.ItemIsEditable)

                    remain = int(CONSTANTS["max_non_active_period"]) - info[i][j + 1]
                    if remain <= 2:
                        self.paint_column(i, j, red if remain <= 0 else light_red)
                else:
                    if j == 4:  # Подсчет возраста клиента в зависимости от его даты рождения
                        item = calculate_age(dt.date(*map(int, info[i][j].split('.'))))
                    else:
                        item = str(info[i][j])
                    self.client_base_table.setItem(i, j, QTableWidgetItem(item))
                    self.client_base_table.item(i, j).setFlags(Qt.ItemIsEditable)
                    self.client_base_table.item(i, j).setForeground(QColor('black'))

                    # Если на ячейках пороговые значения, то красим ячейку
                    if j in (5, 6) and info[i][j] <= 2:
                        self.paint_column(i, j, red if info[i][j] <= 0 else light_red)
                    #
        #

    def load_income_table(self):
        """ Загрущка таблицы клиентов, посетивших занятие """

        self.clients_delete_buttons = []

        # Подготовка данных для таблицы
        date = self.calendar.selectedDate().toString('yyyy.MM.dd')
        id__time__client_id = [res for res in
                               get_data_from_db(MY_DB, 'clients_attendance',
                                                'id, time, client_id', {'date': [date]})]
        table_id = [str(el[0]) for el in id__time__client_id]
        times = [str(el[1]) for el in id__time__client_id]
        clients_id = [str(el[2]) for el in id__time__client_id]
        info = []
        for i, c_id in enumerate(clients_id):
            name = get_data_from_db(MY_DB, 'clients', 'name', {'id': [c_id]})[0][0]
            info.append((table_id[i], times[i], name))
        print(info)
        print('-' * 40)
        self.incoming_clients_table.setRowCount(0)
        #

        # Загрузка строк в таблицу
        for i in range(len(info)):
            self.incoming_clients_table.setRowCount(self.incoming_clients_table.rowCount() + 1)
            for j in range(len(info[0]) + 1):
                if j == 0:  # Установка кнопки для удаления строки
                    btn = QPushButton(delete_char, self)
                    btn.clicked.connect(self.delete_row_from_incoming_clients_table)
                    if (not can_delete_previous_history and
                            dt.date(*map(int, date.split('.'))) < dt.date.today()):
                        btn.setEnabled(False)
                    self.clients_delete_buttons.append(btn)

                    self.incoming_clients_table.setCellWidget(i, j, btn)
                else:
                    self.incoming_clients_table.setItem(i, j, QTableWidgetItem(str(info[i][j - 1])))
                    self.incoming_clients_table.item(i, j).setFlags(Qt.ItemIsEditable)
                    self.incoming_clients_table.item(i, j).setForeground(QColor('black'))
        #

    def load_lessons_table(self):
        """ Загрузка таблицы занятий """

        self.lessons_delete_buttons = []
        self.lessons_time_intervals = []

        date = self.calendar.selectedDate().toString('yyyy.MM.dd')

        # Подготовка данных для таблицы
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
        #

        # Загрузка строк в таблицу
        for i in range(len(info)):
            self.lessons_table.setRowCount(self.lessons_table.rowCount() + 1)
            for j in range(len(info[0]) + 1):
                if j == len(info[0]):  # Установка кнопки для удаления строки
                    btn = QPushButton(delete_char, self)
                    btn.clicked.connect(self.delete_row_from_lessons_table)
                    if (not can_delete_previous_history and
                            dt.date(*map(int, date.split('.'))) < dt.date.today()):
                        btn.setEnabled(False)
                    self.lessons_delete_buttons.append(btn)

                    self.lessons_table.setCellWidget(i, j, btn)
                    self.lessons_table.setItem(i, j, QTableWidgetItem(""))
                else:
                    if j == 2:  # Установка времени
                        t_func = lambda time: dt.time(*map(int, time.split(':')))
                        self.lessons_time_intervals.append(list(map(t_func, info[i][j].split('-'))))
                    self.lessons_table.setItem(i, j, QTableWidgetItem(str(info[i][j])))
                    self.lessons_table.item(i, j).setFlags(Qt.ItemIsEditable)
                    self.lessons_table.item(i, j).setForeground(QColor('black'))

            # Изменение цвета строки в зависимости от типа занятия
            color = get_data_from_db(MY_DB, 'lesson_types', 'color', {'name': [info[i][1]]})[0][0]
            paintRow(self.lessons_table, i, QColor(color))
            #
        #

    def load_month_report_table(self):
        """ Загрузка таблицы отчетов """

        self.more_statistic_buttons = []

        # Подготовка данныз для таблицы
        year = self.year_cb.currentText()
        info = get_data_from_db(MY_DB, 'month_reports', 'month, clients_amount, total_sum',
                                {'year': [year]}, ordering={'month': 0})
        info += [(i, 0, 0) for i in range(1, 12 + 1) if i not in (el[0] for el in info)]
        info.sort(key=lambda y: y[0])
        print(info)
        total_sum = 0
        #

        # Загрузка строк в таблицу
        for i in range(12):
            for j in range(1, len(info[0])):
                data = str(info[i][j]) if j == 1 else beauty_number(info[i][j])
                self.month_reports_table.setItem(i, j - 1, QTableWidgetItem(data))
                self.month_reports_table.item(i, j - 1).setFlags(Qt.ItemIsEditable)
                self.month_reports_table.item(i, j - 1).setForeground(QColor('black'))
            total_sum += info[i][2]

            # Сокрытие пустых строк в зависимости от настроек
            if int(CONSTANTS['hide_zero_rows_in_statistic']) and list(info[i][1:]) == [0, 0]:
                self.month_reports_table.hideRow(i)
            else:
                self.month_reports_table.showRow(i)
            #

            btn = QPushButton(more_char, self)
            btn.clicked.connect(self.show_more_statistic)
            self.more_statistic_buttons.append(btn)

            # Установка кнопки с подробной статистикой #
            self.month_reports_table.setCellWidget(i, 2, btn)
            self.month_reports_table.setItem(i, 2, QTableWidgetItem(""))
        #

        # Установка итоговой выручки #
        self.outcome_lbl.setText(beauty_number(total_sum) + chr(8381))
    #

    def delete_row_from_incoming_clients_table(self):
        """ Метод удаляет строку из таблицы клиентов, пришедших на занятие """

        # Удаление из таблиц
        delete_row = self.clients_delete_buttons.index(self.sender())
        deleted_id = self.incoming_clients_table.item(delete_row, 1).text()
        date = get_data_from_db(MY_DB, 'clients_attendance', 'date', {'id': [deleted_id]})[0][0]
        print(delete_row, deleted_id)
        #

        # Удаление из бд
        self.clients_delete_buttons.pop(self.clients_delete_buttons.index(self.sender()))
        self.incoming_clients_table.removeRow(delete_row)
        delete_data_from_db(MY_DB, 'clients_attendance', {'id': [deleted_id]})
        #

        # Обновление таблиц
        year, month = date.split('.')[:2]
        update_month_report(month, year)
        self.load_month_report_table()
        #

    def delete_row_from_lessons_table(self):
        """ Метод удаляет строку из таблицы занятий """

        # Удаение из таблицы
        delete_row = self.lessons_delete_buttons.index(self.sender())
        deleted_id = self.lessons_table.item(delete_row, 0).text()
        print(delete_row, deleted_id)
        #

        # Удаление из бд
        self.lessons_time_intervals.pop(delete_row)
        self.lessons_delete_buttons.pop(self.lessons_delete_buttons.index(self.sender()))
        self.lessons_table.removeRow(delete_row)
        delete_data_from_db(MY_DB, 'lessons', {'id': [deleted_id]})
        #

    def fill_lessons_automatically(self):
        """ Заполняет таблицу занятий автоматически в зависимости от расписания (настройки) """

        # Удаление строк из таблицы и бд
        date = self.calendar.selectedDate()
        day = date.dayOfWeek()
        date = f"'{date.toString('yyyy.MM.dd')}'"

        delete_data_from_db(MY_DB, 'lessons', {'date': [date[1:-1]]})
        #

        # Обновление данных о занятиях в бд и загрузка таблицы
        for lesson in get_data_from_db(MY_DB, 'lessons_timetable', '*', {'date': [str(day)]}):
            lesson = list(map(lambda el: f'"{el}"', lesson[1:]))
            lesson[0] = date
            add_data_to_db(MY_DB, 'lessons', ('date', 'time', 'lesson_type_id'), lesson)

        self.load_lessons_table()
        #

    def sort_table(self, index):
        """ Метод сортирует таблицу клиентов по колонке """

        if index == 2:  # Запрет сортировать по номеру телефона
            return

        if self.ordering_index != index:  # Определение типа сортировки (по возрастанию/по убыванию
            self.ordering = False

        # Получение информации с учетом фильтра по имени
        if self.is_name_filtered:
            info = get_data_from_db(MY_DB, 'clients', '*',
                                    conditions_like={'name': '%' + self.search_line.text() + '%'})
        else:
            info = get_data_from_db(MY_DB, 'clients', '*')
        #

        # Сортировка данных
        if index in (3, 4):
            key_func = lambda y: dt.date(*map(int, y[index].split('.')))
        else:
            key_func = lambda y: y[index]
        rev = self.ordering if index != 4 else not self.ordering
        sorted_info = sorted(info, key=key_func, reverse=rev)
        #

        # Обновление информации о сортировке
        self.ordering = not self.ordering
        self.ordering_index = index
        #

        self.load_client_table(sorted_info)  # Загрузка таблицы клиентовс отсортированными данными

    def search_by_name(self):
        """ Метод осуществляет поиск по ФИО клиентов (чувствителен к регистру) """

        request = self.search_line.text()

        if len(request) > 1:  # Если букв для поиске 2 или больше
            info = get_data_from_db(MY_DB, 'clients', '*', conditions_like={'name': f'%{request}%'})
            self.is_name_filtered = True
        else:
            info = get_data_from_db(MY_DB, 'clients', '*')
            self.is_name_filtered = False

        self.load_client_table(info)  # Загрузка таблицы клиентов с отфильтрованными данными

    # Методы для обновления данных
    def update_current_row(self, row, col):
        """ Метод окрашивает текущую выбранную строку в таблице клиентов """

        if self.cur_row != -1:
            paintRow(self.client_base_table, self.cur_row[0], Qt.transparent, True)
        self.cur_row = (row, col)
        paintRow(self.client_base_table, row, light_blue, True)

    def update_client_activity(self):
        """ Обновляет состояние активности клиента в таблице клиентов """

        if self.sender().isChecked():  # Запрос подтверждения действия
            text = f'Вы действительно хотите вернуть активность этого клиента?'
            valid = QMessageBox.question(self, '', text, QMessageBox.Yes, QMessageBox.No)

            if valid == QMessageBox.No:  # Если дейтсвие не подтверждено сбрасываем checkbox
                self.load_client_table()
                return

        # Обновляем активность клиента и записи в бд
        my_row = self.client_activate_checkboxes.index(self.sender())
        client_id = self.client_base_table.item(my_row, 0).text()
        update_data_in_db(MY_DB, 'clients',
                          {'is_active': int(self.sender().isChecked()), 'non_active_days': '0'},
                          {'id': client_id})
        #
        self.load_client_table()  # Загрузка таблицы клиентов

    def update_planner_tab_tables(self):
        """ Обновление таблиц занятий и клиентов, посетивших занятия """

        self.load_lessons_table()
        self.load_income_table()

    def update_year_statistic(self):
        """ Метод обновляет годовую статистику """
        self.load_month_report_table()
    #

    def paint_column(self, row, col, color: QColor):
        """ Метод окрашивает ячейку таблицы клиентов в указанный цвет """
        self.client_base_table.item(row, col).setBackground(color)

    def closeEvent(self, event) -> None:
        """ Обновление даты последней активности при закрытии приложения """

        date = f"'{dt.date.today().strftime('%Y.%m.%d')}'"
        update_data_in_db(MY_DB, 'settings', {'value': date}, {'param': 'last_activity_date'})

        sys.exit()


def paintRow(table: QTableWidget, row: int, color: QColor, save_color=False):
    """ Функция окрашивает строку таблицы table в указанный цвет """

    for col in range(table.columnCount()):
        cell_color = table.item(row, col).background().color().name()

        # При необходимости сохранять цвет некоторых ячеек строки (save_color),
        # данные ячейки сохраняют свой цвет
        if not save_color or cell_color in (transparent.name(), light_blue.name()):
            table.item(row, col).setBackground(color)


def calculate_age(born: dt.date) -> str:
    """ Функция считает возраст, основываясь на дате рождения """
    today = dt.date.today()
    return str(today.year - born.year - ((today.month, today.day) < (born.month, born.day)))


def calculate_time(cur_hour: int, cur_min: int, minutes: int):
    """ Подсчет время конца действия, учитывая начальное время и длительность действия """

    end_sec = (dt.timedelta(hours=cur_hour, minutes=cur_min) +
               dt.timedelta(minutes=minutes)).seconds
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
    """ Функция обновляет словарь констант """
    global CONSTANTS
    CONSTANTS = dict(get_data_from_db(MY_DB, 'settings', 'param, value'))


def update_app(playlist: pyglet.media):
    """ Метод обновляет app для воспроизведения звуковых файлов """

    global play_time
    play_time += 0.5  # Функция вызывается каждые 0.5 секунды

    # Завершает воспроизведение звукового файла,
    # если он закончился или превышено максимальное время воспроизведения
    if not playlist.playing or play_time > MAX_SOUND_DURATION_SECONDS:
        play_time = 0
        playlist.pause()
        pyglet.clock.unschedule(update_app)
        pyglet.app.exit()
    #


def play_sound(sound):
    """ Метод воспроизводит звуковой файл """

    player = pyglet.media.Player()
    player.queue(sound)
    player.play()

    # Устанавка обновления app для файла #
    pyglet.clock.schedule_interval(lambda el: update_app(player), 0.5)
    pyglet.app.run()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Обновление констант и начальных значений
    update_constants()
    update_data_in_new_day()
    update_month_report(str(dt.date.today().month), str(dt.date.today().year))
    #

    wnd = MainWindow()
    wnd.show()

    sys.excepthook = except_hook
    sys.exit(app.exec())
