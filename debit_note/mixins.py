from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect

from debit_note.forms import IssuerCompanyFormset, CurrencyFormset, CurrencyCreateForm, PaymentMethodFormset, \
    PaymentMethodCreateForm
from debit_note.models import DebitNote, IssuerCompany, Currency, PaymentMethod


class CompanyCreatorPermissionMixin(UserPassesTestMixin):

    def test_func(self):
        if self.get_object().company_creator == self.request.user.company:
            return HttpResponseForbidden()


class DebitNoteFilterMixin:

    def get_all_years(self):
        queryset = DebitNote.objects.all().values('issue_date__year').distinct()
        all_years = list()
        for query in queryset:
            for key, year in query.items():
                all_years.append(str(year))
        return all_years

    def get_all_months(self):
        queryset = DebitNote.objects.all().values('issue_date').distinct()
        all_dates = list()
        all_months_int = list()
        for query in queryset:
            for key, value in query.items():
                if not value.month in all_months_int:
                    all_dates.append(value)
                    all_months_int.append(value.month)
        return all_dates

    def filter_get_queryset(self):
        queryset = DebitNote.objects.filter(company_creator=self.request.user.company)
        queries = []
        if self.request.GET.get('year'):
            queries.append(Q(issue_date__year__in=self.request.GET.getlist('year')))
        if self.request.GET.get('month'):
            queries.append(Q(issue_date__month__in=self.request.GET.getlist('month')))
        if self.request.GET.get('is_paid'):
            queries.append(Q(is_paid__in=self.request.GET.getlist('is_paid')))
        for query in queries:
            queryset = queryset.filter(query)
        return queryset

    def filter_get_context(self):
        filter_context = dict()
        if self.request.GET.getlist('year'):
            for year in self.request.GET.getlist('year'):
                filter_context[year] = year
        if self.request.GET.getlist('month'):
            for month in self.request.GET.getlist('month'):
                filter_context[month] = month
        if self.request.GET.getlist('is_paid'):
            for status in self.request.GET.getlist('is_paid'):
                if status == 'True':
                    filter_context['true'] = status
                if status == 'False':
                    filter_context['false'] = status
        return filter_context


class DebitNoteSettingsMixin:
    models = [
        {IssuerCompany: ('Продавцы', IssuerCompanyFormset, None)},
        {Currency: ('Валюты', CurrencyFormset, CurrencyCreateForm)},
        {PaymentMethod: ('Методы оплаты', PaymentMethodFormset, PaymentMethodCreateForm)}
    ]
    option_kwarg = 'option'
    action_kwarg = 'action'
    create_kwarg = 'create'
    update_kwarg = 'update'

    def __init__(self):
        super().__init__()
        self.__option_param = None
        self.__action_param = None

    @property
    def options(self):
        options = dict()
        for model in self.models:
            for model_name, forms in model.items():
                options[model_name.__name__.lower()] = {
                    f'{self.update_kwarg}': forms[1],
                    f'{self.create_kwarg}': forms[2],
                    'verbose_name': forms[0]
                }
        return options

    def setup(self, request, *args, **kwargs):
        self.__option_param = request.GET.get(self.option_kwarg)
        self.__action_param = request.GET.get(self.action_kwarg)
        super().setup(request, *args, **kwargs)

    def get_context_data(self):
        context = dict()
        context['option_kwarg'] = self.option_kwarg
        context['action_kwarg'] = self.action_kwarg
        context['update_kwarg'] = self.update_kwarg
        context['create_kwarg'] = self.create_kwarg
        context['options'] = dict()
        for option in self.options:
            context['options'][option] = {
                'name': option,
                'queryset': self.get_queryset_by_option_name(option),
                'verbose_name': self.options[option]['verbose_name']
            }
            if not self.options[option][f'{self.create_kwarg}']:
                context['options'][option].update({'not_create_option': True})
        return context

    @property
    def option_param(self):
        return self.__option_param

    @property
    def action_param(self):
        return self.__action_param

    def get_queryset_by_option_name(self, option_name):
        if self.options[option_name][f'{self.update_kwarg}']:
            model = self.options[option_name][f'{self.update_kwarg}'].model
        else:
            model = self.options[option_name][f'{self.create_kwarg}'].Meta.model
        return model.objects.filter(company_creator=self.request.user.company)

    def make_action(self):
        context = self.get_context_data()
        context['option_param'] = self.option_param
        context['make_action'] = self.action_kwarg
        context['action_param'] = self.action_param
        if self.action_param == self.update_kwarg:
            context['formset'] = self.options[self.option_param][self.action_param](
                queryset=self.get_queryset_by_option_name(self.option_param))
        if self.action_param == self.create_kwarg:
            context['form'] = self.options[self.option_param][self.action_param]()
        return render(self.request, 'debit_note/note_settings.html', context)

    def show_all_options(self):
        context = self.get_context_data()
        return render(self.request, 'debit_note/note_settings.html', context)

    def get(self, *args, **kwargs):
        if not self.option_param or (not self.get_queryset_by_option_name(
                self.option_param).exists() and self.action_param == self.update_kwarg):
            return self.show_all_options()
        return self.make_action()

    def post(self, *args, **kwargs):
        option = self.option_param
        action = self.action_param
        if action == self.create_kwarg:
            form = self.options[option][action](self.request.POST)
            if form.is_valid():
                new_instance = form.save(commit=False)
                new_instance.company_creator = self.request.user.company
                new_instance.save()
                return redirect('note_settings')
        if action == self.update_kwarg:
            formset = self.options[option][action](self.request.POST, self.get_queryset_by_option_name(option))
            if formset.is_valid():
                formset.save()
                return redirect('note_settings')
        return self.make_action()
