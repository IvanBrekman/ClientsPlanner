import datetime as dt


class FormatError(Exception):
    def message(self):
        return 'Неверный формат номера телефона.'


class LenNumberError(Exception):
    def message(self):
        return 'Неверное количество цифр в номере телефона.'


class NameFormatError(Exception):
    def message(self):
        return f'                                       Неверный формат ФИО.\n' \
               f'Должно присутствовать хотя бы имя и фамилия, разделенные пробелом.'


class DigitInNameError(Exception):
    def message(self):
        return 'Неверный формат ФИО. Присутствуют числа или другие недопустимые символы.'


class BusyTimeError(Exception):
    def message(self):
        return 'В данное время уже проходит занятие. Выберите другое время.'


class WrongEndTimeError(Exception):
    def message(self):
        return 'Время окончания раньше времени начала или совпадает с ним. Выберите другое время.'


def convert_number(number: str) -> str:
    """
    Проверяет номер телефона и преобразует его к единому формату: +79998889988
    При введении некорректного номера телефона возвращает строковую ошибку
    """

    number = number.strip()
    if number.startswith('8') or number.startswith('7'):
        number = number.replace(number[0], '+7', 1)

    try:
        copy_number = number.replace(' ', '')
        if not copy_number.startswith('+7'):
            raise FormatError

        if len(copy_number) < 4:
            raise LenNumberError

        if copy_number[3] == '-' or copy_number[-1] == '-' or '--' in copy_number:
            raise FormatError

        if number.count('(') > 1 or number.count(')') > 1 or not check_correct_bracket_seq(number):
            raise FormatError

        number = number.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        number = number.replace('\t', '')

        if len(number) != 12:
            raise LenNumberError

        int(number)
    except ValueError:
        return 'неверный формат'
    except FormatError as fe:
        return fe.message()
    except LenNumberError as see:
        return see.message()

    return number


def check_correct_bracket_seq(checked_sequence: str) -> bool:
    count = 0
    for el in checked_sequence:
        if el == '(':
            count += 1
        elif el == ')':
            count -= 1

        if count < 0:
            return False

    return count == 0


def convert_name(name: str) -> str:
    """
    Проверка корректности ФИО. Возвращает ФИО в формате: Фамилия Имя Отчество
    При введении некорректного ФИО возвращает строковую ошибку
    """

    try:
        if len(name) == 0 or len(name.split(' ')) < 2:
            raise NameFormatError
        if not all(sym.isalpha() for sym in name.replace(' ', '')):
            raise DigitInNameError

        name = ' '.join(map(str.capitalize, name.split()))
        return name
    except NameFormatError as nfe:
        return nfe.message()
    except DigitInNameError as dine:
        return dine.message()


def check_correct_time(start_time: dt.time, end_time: dt.time, time_intervals: list) -> (bool, str):
    """
    Проверка корректности переданного времени.
    Проверяет также не пересекается ли введенное время с временем из списка time_intervals
    В случае некорректного времени возвращает строковую ошибку
    """

    try:
        if start_time >= end_time:
            raise WrongEndTimeError
        if any([t[0] <= start_time < t[1] or t[0] < end_time <= t[1] for t in time_intervals]):
            raise BusyTimeError
    except WrongEndTimeError as wete:
        return wete.message()
    except BusyTimeError as bte:
        return bte.message()
    return True


if __name__ == '__main__':
    while True:
        phone = input()
        print(convert_number(phone))
