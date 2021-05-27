import datetime as dt
from collections import Counter

from database_requests import *

"""
        Данный модуль реализует функции обновления данных в бд
"""

MY_DB = "clients.db"


def update_data_in_new_day() -> None:
    """
    Обновляет информацию в базе данных, если текущий день не совпадает с днем последней активности
    """

    today = dt.date.today()
    params = (MY_DB, 'settings', 'value', {'param': ['last_activity_date']})
    last_session = dt.date(*map(int, get_data_from_db(*params)[0][0].split('.')))
    # last_session = dt.date(2020, 12, 1) для проверки модуля
    
    if today != last_session:
        update_lessons_amount(last_session, today)
        update_lessons_and_non_active_duration(last_session, today)


def update_lessons_amount(last_session: dt.date, today: dt.date) -> None:
    """ Обновление количества занятий у всех активныз пользователей """

    all_clients_id = Counter()
    for d in date_range(last_session, today):
        d = d.strftime('%Y.%m.%d')
        clients_id = [res[0] for res in get_data_from_db(MY_DB, 'clients_attendance', 'client_id',
                                                         {'date': [d]})]
        all_clients_id += Counter(clients_id)
    print(all_clients_id)
    for client_id in all_clients_id:
        update_data_in_db(MY_DB, 'clients',
                          {'lessons_amount': f'lessons_amount - {all_clients_id[client_id]}'},
                          {'id': client_id})


def update_lessons_and_non_active_duration(last_session: dt.date, today: dt.date) -> None:
    """ Обновление длительности абонемента и длительности неактивного периода клиента """

    days_number = len(list(date_range(last_session, today)))
    update_data_in_db(MY_DB, 'clients', {'duration': f'duration - {days_number}'}, {'is_active': 1})
    update_data_in_db(MY_DB, 'clients', {'non_active_days': f'non_active_days + {days_number}'},
                      {'is_active': 0})


def update_month_report(month_num: str, year_num: str) -> None:
    """ Обновление отчета при: 1) Добавлении/удалении клиента, 2) Внесении/удалении оплаты """

    clients = get_data_from_db(MY_DB, 'clients_attendance', 'id',
                               conditions_like={'date': f'{year_num}.{month_num.rjust(2, "0")}.%'})
    pays = get_data_from_db(MY_DB, 'payments_table', 'pay_sum',
                            conditions_like={'date': f'{year_num}.{month_num.rjust(2, "0")}.%'})
    clients_amount = str(len(clients))
    total_sum = str(sum(pay[0] for pay in pays))

    if get_data_from_db(MY_DB, 'month_reports', 'id', {'year': [year_num], 'month': [month_num]}):
        update_data_in_db(MY_DB, 'month_reports',
                          {'clients_amount': clients_amount, 'total_sum': total_sum},
                          {'year': year_num, 'month': month_num})
    else:
        add_data_to_db(MY_DB, 'month_reports', ('year', 'month', 'clients_amount', 'total_sum'),
                       (year_num, month_num, clients_amount, total_sum))


def date_range(start_date: dt.date, end_date: dt.date) -> iter:
    """ Генератор периода даты от начальной включительно, до конечной не включительно """

    while start_date < end_date:
        yield start_date
        start_date += dt.timedelta(days=1)


if __name__ == '__main__':
    ####
    # !!! Внимание, данный код моежт изменить состояние базы данных, запускать только осознанно !!!
    print(*date_range(dt.date(2020, 11, 1), dt.date(2020, 12, 5)), sep='\n')
    update_month_report('12', '2020')
    ####
