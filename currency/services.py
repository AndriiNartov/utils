from datetime import datetime, timedelta

import requests


CURRENCY_API_REQUEST_URL = 'http://api.nbp.pl/api/exchangerates/rates/A/EUR/'


def get_exc_rate_info_for_date(date):
    response = requests.get(f'{CURRENCY_API_REQUEST_URL}{date}/')
    if response.status_code == 200:
        response_dict = response.json()
        eur_exc_rate = str(response_dict['rates'][0]['mid'])
        table_number = response_dict['rates'][0]['no']
        if len(eur_exc_rate.split('.')[1]) == 2:
            eur_exc_rate += '00'
        if len(eur_exc_rate.split('.')[1]) == 3:
            eur_exc_rate += '0'
        return eur_exc_rate, table_number


def make_text_for_paste(date):
    try:
        eur_exc_rate, table_number = get_exc_rate_info_for_date(date)
        return f'Tabela nr {table_number} z dnia {date}\n\nKURS: 1 EUR = {eur_exc_rate} PLN'
    except:
        return 'Нет курса на заданную дату!'


def get_closest_prev_workday(datetime_date_today):
    for prev_date_delta in range(1, 8):
        prev_date = datetime_date_today - timedelta(prev_date_delta)-timedelta(1)
        prev_date_str = datetime.strftime(prev_date, '%Y-%m-%d')
        response = requests.get(f'{CURRENCY_API_REQUEST_URL}{prev_date_str}/')
        if response.status_code == 200:
            return prev_date, make_text_for_paste(prev_date_str)


def parse_text_to_get_date(text):
    splitted_text = text.split(' ')
    for list_el in splitted_text:
        if 'KURS' in list_el:
            date = list_el[:10]
            return date
