from django.contrib import admin

from .models import *
from account.models import Address

admin.site.register(DebitNote)
admin.site.register(Position)
admin.site.register(IssuerCompany)
admin.site.register(PurchaserCompany)
admin.site.register(Currency)
admin.site.register(PaymentMethod)
admin.site.register(Address)
admin.site.register(BankAccount)


