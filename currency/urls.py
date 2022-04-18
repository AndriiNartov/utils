from django.urls import path

from .views import get_currency_exchange_rate


urlpatterns = [
    path('', get_currency_exchange_rate, name='currency'),
]