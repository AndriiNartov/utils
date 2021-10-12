from datetime import timedelta, datetime

from django.db import models
from django.db.models import Sum

from account.models import User, Company, MainCompany


def payment_deadline_date_count(issue_date, payment_period):
    delta = timedelta(days=payment_period)
    payment_deadline_date = issue_date + delta
    return payment_deadline_date


def make_chosen_by_default_attribute_unique(instance):
    if instance.chosen_by_default:
        instance.__class__.objects \
            .filter(chosen_by_default=True, company_creator=instance.company_creator) \
            .update(chosen_by_default=False)


class MainCompanyInfo(models.Model):
    company_creator = models.ForeignKey(
        MainCompany,
        on_delete=models.SET_NULL,
        verbose_name='Создал(компания)',
        blank=True,
        null=True
    )

    class Meta:
        abstract = True


class DebitNote(MainCompanyInfo):
    number = models.CharField(max_length=20, verbose_name='Номер', editable=True)
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания ноты')
    issue_date = models.DateField(verbose_name='Дата выставления')
    payment_period = models.PositiveSmallIntegerField(verbose_name='Срок оплаты', default=60)
    payment_deadline_date = models.DateField(verbose_name='Дата оплаты', blank=True, null=True, editable=False)
    total_amount = models.PositiveSmallIntegerField(verbose_name='Сумма к оплате', default=0, editable=False, blank=True)
    currency = models.CharField(max_length=3, default='EUR', verbose_name='Валюта')
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='Выставил(сотрудник)', blank=True, null=True)
    issuer_company = models.ForeignKey('IssuerCompany', on_delete=models.SET_NULL, verbose_name='Предоставитель услуги', null=True)
    purchaser_company = models.ForeignKey('PurchaserCompany', on_delete=models.SET_NULL, verbose_name='Плательщик', null=True)
    payment_method = models.ForeignKey('PaymentMethod', on_delete=models.SET_NULL, verbose_name='Форма платежа', null=True)
    is_paid = models.BooleanField(default=False, blank=True, verbose_name='Оплачено')
    bank_account = models.ForeignKey('BankAccount', on_delete=models.SET_NULL, verbose_name='Банковский счёт', null=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.issue_date:
            self.issue_date = datetime.now()
        self.payment_deadline_date = payment_deadline_date_count(self.issue_date, self.payment_period)

        if not self.positions.all():
            self.total_amount = 0
        else:
            all_positions_amount_sum = self.positions.all().aggregate(total_amount=Sum('amount'))['total_amount']
            self.total_amount = all_positions_amount_sum
        super().save()

    def __str__(self):
        return f'{self.number} | {self.company_creator}'

    class Meta:
        ordering = ('company_creator', 'id')


class IssuerCompany(Company, MainCompanyInfo):
    tax_id = models.CharField(max_length=50, verbose_name='Налоговый номер')
    chosen_by_default = models.BooleanField(default=False, blank=True, verbose_name='Выбрать по умолчанию')
    invitation_link_suffix = None

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        make_chosen_by_default_attribute_unique(self)
        super().save()

    class Meta:
        constraints = [models.UniqueConstraint(fields=['tax_id', 'company_creator'], name='unique_issuer')]


class PurchaserCompany(Company, MainCompanyInfo):
    tax_id = models.CharField(max_length=50, verbose_name='Налоговый номер')
    phone = None

    def __str__(self):
        return f'{self.name}, {self.address}, NIP: {self.tax_id}'

    class Meta:
        constraints = [models.UniqueConstraint(fields=['tax_id', 'company_creator'], name='unique_purchaser')]


class BankAccount(models.Model):
    owner = models.ForeignKey(
        IssuerCompany,
        on_delete=models.CASCADE,
        verbose_name='Владелец счёта',
        blank=True,
        null=True,
        related_name='bank_accounts'
    )
    name = models.CharField(max_length=30, verbose_name='Название')
    account_number = models.CharField(max_length=50, verbose_name='Номер счета')
    bank_name = models.CharField(max_length=100, verbose_name='Название банка', blank=True, null=True)
    extra_parameters = models.CharField(max_length=100, verbose_name='Дополнительные параметры')

    def __str__(self):
        return f'{self.owner}: {self.name} {self.account_number}'


class Currency(MainCompanyInfo):
    name = models.CharField(max_length=3, verbose_name='Валюта')
    chosen_by_default = models.BooleanField(default=False, blank=True, verbose_name='Выбрать по умолчанию')

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        make_chosen_by_default_attribute_unique(self)
        super().save()


class PaymentMethod(MainCompanyInfo):
    name = models.CharField(max_length=50, verbose_name='Название')
    chosen_by_default = models.BooleanField(default=False, blank=True, verbose_name='Выбрать по умолчанию')

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        make_chosen_by_default_attribute_unique(self)
        super().save()


class Position(models.Model):
    debit_note = models.ForeignKey(
        DebitNote,
        on_delete=models.CASCADE,
        verbose_name='Позиция',
        related_name='positions',
        blank=True,
        null=True
    )
    description = models.CharField(max_length=250, verbose_name='Описание')
    amount = models.PositiveSmallIntegerField(verbose_name='Сумма')
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, verbose_name='Валюта')

