from datetime import datetime

from django.shortcuts import render

from .forms import ExchangeRateDateForm, TextFieldForCopyForm
from .services import get_closest_prev_workday, make_text_for_paste, parse_text_to_get_date


def get_currency_exchange_rate(request):
    form = ExchangeRateDateForm()
    text_area_form = TextFieldForCopyForm()
    prev_workday_date, text = get_closest_prev_workday(datetime.utcnow().date())
    form.fields['date'].initial = prev_workday_date
    text_area_form.fields['text'].initial = text
    date_format = '%Y-%m-%d'
    if request.GET.get('text'):
        text = request.GET.get('text')
        date = parse_text_to_get_date(text)
        if not date:
            return render(request, 'currency/get_rate.html', {'form': form, 'text_area_form': text_area_form})
        form.fields['date'].initial = datetime.strptime(date, date_format).date()
        text_area_form.fields['text'].initial = make_text_for_paste(datetime.strftime(datetime.strptime(date, date_format).date(), date_format))
    if request.GET.get('date'):
        chosen_date = datetime.strptime(request.GET.get('date'), date_format).date()
        form.fields['date'].initial = chosen_date
        text_area_form.fields['text'].initial = make_text_for_paste(str(chosen_date))
    return render(request, 'currency/get_rate.html', {'form': form, 'text_area_form': text_area_form})
