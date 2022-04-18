from datetime import datetime

from zeep import Client
from zeep.wsse import UsernameToken

from .models import Letter

API_POST_CLIENT = Client(
    wsdl='https://tt.poczta-polska.pl/Sledzenie/services/Sledzenie?wsdl',
    wsse=UsernameToken('sledzeniepp', 'PPSA')
)


def reformat_date(date_time_str_obj):
    date_without_time = date_time_str_obj.split(' ')[0]
    new_date = datetime.strptime(date_without_time, '%Y-%m-%d')
    return new_date


def get_undelivered_letters():
    undelivered_letters_queryset = Letter.objects.exclude(status=Letter.SUCCESSFULLY_DELIVERED)
    return undelivered_letters_queryset


def set_status_for_letter():
    undelivered_letters = get_undelivered_letters()
    for letter in undelivered_letters:
        if letter.track_number == 'b/n':
            letter.status = Letter.ON_THE_WAY
            letter.status_date = letter.sending_date
            continue
        requested_letter = API_POST_CLIENT.service.sprawdzPrzesylke(letter.track_number)
        status_list = []
        if not requested_letter.danePrzesylki.zdarzenia:
            letter.status = Letter.DO_NOT_TRACK
            letter.status_date = letter.sending_date
            letter.save()
            continue
        for zdarzenie in requested_letter.danePrzesylki.zdarzenia.zdarzenie:
            status_list.append(zdarzenie.nazwa)
        if 'Wysłanie przesyłki z kraju nadania' in status_list:
            letter.status = Letter.ON_THE_WAY
            letter.status_date = reformat_date(zdarzenie.czas)
        if 'Doręczenie' in status_list or 'Odebranie w urzędzie' in status_list:
            letter.status = Letter.SUCCESSFULLY_DELIVERED
            letter.status_date = reformat_date(zdarzenie.czas)
            letter.save()
            continue
        if 'Awizo' in status_list:
            letter.status = Letter.RECIPIENT_IS_NOT_AVAILABLE
            letter.status_date = reformat_date(zdarzenie.czas)
            letter.save()
            continue
        if 'Wprowadzenie do księgi oddawczej' in status_list:
            letter.status = Letter.HAS_TO_BE_DELIVERED_TODAY
            letter.status_date = reformat_date(zdarzenie.czas)
            letter.save()
            continue
