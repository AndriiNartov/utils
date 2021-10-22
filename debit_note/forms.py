import datetime

from django import forms
from django.forms import inlineformset_factory, modelformset_factory

from account.models import MainCompany
from .models import DebitNote, Position, IssuerCompany, PurchaserCompany, Currency, PaymentMethod, BankAccount


class PositionCreateForm(forms.ModelForm):
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'rows': 1,
                'placeholder': ''
            }
        ),
        label='Описание/причина выставления ноты'
    )
    currency = forms.ModelChoiceField(
        widget=forms.Select,
        queryset=Currency.objects.all(),
        label='Валюта',
    )
    amount = forms.CharField(
        widget=forms.NumberInput(
            attrs={
                'style': 'width: 70px',
                'placeholder': ''
            }
        )
    )

    class Meta:
        model = Position
        exclude = ('debit_note',)


class DebitNoteCreateForm(forms.ModelForm):

    issue_date = forms.DateField(
        widget=forms.TextInput(attrs={'type': 'date'}),
        initial=datetime.datetime.now().date(),
        label='Дата выставления'
    )
    purchaser_company = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'id': 'tax_id',
                'autocomplete': 'off'
            }),
        label='Плательщик',
    )
    issuer_company = forms.ModelChoiceField(
        widget=forms.Select,
        queryset=IssuerCompany.objects.all(),
        label='Выставил'
    )
    bank_account = forms.ModelChoiceField(
        widget=forms.Select,
        queryset=BankAccount.objects.all(),
        label='Номер счёта',
    )
    payment_method = forms.ModelChoiceField(
        widget=forms.Select,
        queryset=PaymentMethod.objects.all(),
        label='Способ оплаты',
    )

    def __init__(self, *args, **kwargs):
        self.company_creator = kwargs.pop('company_creator')
        super().__init__(*args, **kwargs)
        self.fields['issuer_company'].queryset = IssuerCompany.objects.filter(company_creator=self.company_creator)
        self.fields['bank_account'].queryset = BankAccount.objects.filter(owner__company_creator=self.company_creator)
        self.fields['payment_method'].queryset = PaymentMethod.objects.filter(company_creator=self.company_creator)
        self.fields['purchaser_company'].widget.attrs['data-creator'] = self.company_creator.pk

    def clean_bank_account(self):
        bank_account_from_filed = self.cleaned_data['bank_account']
        issuer_company_from_field = self.cleaned_data['issuer_company']
        if not bank_account_from_filed.owner == issuer_company_from_field:
            raise forms.ValidationError('Номер счёта должен принадлежать фирме, от имени которой выставляется нота')
        return bank_account_from_filed

    def clean_purchaser_company(self):
        purchaser_company = self.cleaned_data['purchaser_company']
        tax_id = purchaser_company.split(',')[0].split(' ')[1]
        try:
            return PurchaserCompany.objects.get(tax_id=tax_id, company_creator=self.company_creator)
        except:
            raise forms.ValidationError(f'В базе Ваших клиентов нет компании с налоговым номером {tax_id}')

    class Meta:
        model = DebitNote
        fields = ('issue_date', 'payment_period', 'issuer_company', 'purchaser_company', 'payment_method', 'bank_account')


class PurchaserCompanyCreateForm(forms.ModelForm):
    tax_id = forms.CharField(widget=forms.TextInput(attrs={'class': 'col-form-label'}), label='Налоговый номер')
    company_creator = forms.ModelChoiceField(widget=forms.HiddenInput, queryset=MainCompany.objects.all())

    def clean(self):
        super().clean()
        tax_id = self.cleaned_data['tax_id']
        company_creator = self.cleaned_data['company_creator']
        if PurchaserCompany.objects.filter(tax_id=tax_id, company_creator=company_creator).exists():
            errors = {'tax_id': forms.ValidationError('Покупатель c таким налоговым номером уже есть в базе Ваших клиентов', code='purchaser_exists')}
            raise forms.ValidationError(errors)

    class Meta:
        model = PurchaserCompany
        fields = ('name', 'tax_id', 'company_creator')


class PurchaserCompanyUpdateForm(forms.ModelForm):
    tax_id = forms.CharField(widget=forms.TextInput(attrs={'class': 'col-form-label'}), label='Налоговый номер')
    company_creator = forms.ModelChoiceField(widget=forms.HiddenInput, queryset=MainCompany.objects.all())

    class Meta:
        model = PurchaserCompany
        fields = ('name', 'tax_id', 'company_creator')


class IssuerCompanyUpdateForm(forms.ModelForm):
    tax_id = forms.CharField(widget=forms.TextInput, label='Налоговый номер')
    company_creator = forms.ModelChoiceField(widget=forms.HiddenInput, queryset=MainCompany.objects.all())
    chosen_by_default = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput,
        label='Выбрать по умолчанию для всех новых нот'
    )

    class Meta:
        model = IssuerCompany
        fields = ('name', 'tax_id', 'chosen_by_default', 'phone', 'company_creator')


class IssuerCompanyCreateForm(IssuerCompanyUpdateForm):
    company_creator = forms.ModelChoiceField(widget=forms.HiddenInput, queryset=MainCompany.objects.all())

    def clean(self):
        super().clean()
        print(self.cleaned_data)
        tax_id = self.cleaned_data['tax_id']
        company_creator = self.cleaned_data['company_creator']
        if IssuerCompany.objects.filter(tax_id=tax_id, company_creator=company_creator).exists():
            errors = {'tax_id': forms.ValidationError('Продавец c таким налоговым номером уже есть в базе', code='issuer_exists')}
            raise forms.ValidationError(errors)


class BankAccountCreateForm(forms.ModelForm):
    extra_parameters = forms.CharField(required=False, label='Доп. параметры')

    class Meta:
        model = BankAccount
        fields = ('name', 'account_number', 'bank_name', 'extra_parameters')


class CurrencyCreateForm(forms.ModelForm):
    company_creator = forms.ModelChoiceField(required=False, widget=forms.HiddenInput, queryset=MainCompany.objects.all())
    name = forms.CharField(label='Название')

    class Meta:
        model = Currency
        fields = '__all__'


class PaymentMethodCreateForm(forms.ModelForm):
    company_creator = forms.ModelChoiceField(required=False, widget=forms.HiddenInput, queryset=MainCompany.objects.all())

    class Meta:
        model = PaymentMethod
        fields = '__all__'


PositionInlineFormset = inlineformset_factory(DebitNote, Position, form=PositionCreateForm, extra=1)
PaymentMethodFormset = modelformset_factory(
    PaymentMethod,
    exclude=('company_creator',),
    widgets={
            'chosen_by_default': forms.CheckboxInput(attrs={'id': 'chosen_by_default'})
        },
    extra=0,
    can_delete=True
)
CurrencyFormset = modelformset_factory(
    Currency,
    exclude=('company_creator',),
    widgets={
        'chosen_by_default': forms.CheckboxInput(attrs={'id': 'chosen_by_default'})
    },
    extra=0,
    can_delete=True
)
IssuerCompanyFormset = modelformset_factory(
    IssuerCompany,
    fields=('name', 'chosen_by_default'),
    widgets={
        'name': forms.TextInput(attrs={'readonly': True}),
        'chosen_by_default': forms.CheckboxInput(attrs={'id': 'chosen_by_default'})
    },
    extra=0)
