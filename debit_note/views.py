from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Count, Q
from django.http import HttpResponseRedirect, FileResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from account.models import MainCompany
from .mixins import CompanyCreatorPermissionMixin, DebitNoteFilterMixin, DebitNoteSettingsMixin
from .models import DebitNote, PurchaserCompany, IssuerCompany, BankAccount, PaymentMethod, Currency
from .forms import DebitNoteCreateForm, IssuerCompanyCreateForm, PurchaserCompanyCreateForm, PositionCreateForm, \
    PositionInlineFormset, BankAccountCreateForm, PaymentMethodFormset, CurrencyFormset, IssuerCompanyFormset, \
    PurchaserCompanyUpdateForm, IssuerCompanyUpdateForm, PaymentMethodCreateForm, CurrencyCreateForm
from .services import convert_html_to_pdf, CompanyDetailsFromAPIRequest, set_correct_queryset_for_currency, \
    assign_fields_for_new_note, remove_html_and_pdf_files, purchaser_search_ajax_handling
from account.forms import AddressCreateForm


class DebitNoteCreateView(PermissionRequiredMixin, CreateView):
    model = CreateView
    template_name = 'debit_note/note_create.html'
    form_class = DebitNoteCreateForm
    position_form = PositionCreateForm
    permission_required = ('debit_note.add_debitnote')

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs()
        kwargs['company_creator'] = self.request.user.company
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        position_form = self.position_form(initial={
            'currency': Currency.objects
                .filter(chosen_by_default=True, company_creator=self.request.user.company)
                .first()
        })
        set_correct_queryset_for_currency(position_form, self.request)
        context['position_form'] = position_form
        context['form'] = self.form_class(initial={
            'payment_method': PaymentMethod.objects
                .filter(chosen_by_default=True, company_creator=self.request.user.company)
                .first(),
            'issuer_company': IssuerCompany.objects
                .filter(chosen_by_default=True, company_creator=self.request.user.company)
                .first()
        }, company_creator=self.request.user.company)

        context['url_name'] = self.request.resolver_match.url_name
        tax_id_query_param = self.request.GET.get('tax_id')
        if tax_id_query_param:
            purchaser_company = get_object_or_404(PurchaserCompany.objects.filter(tax_id=tax_id_query_param))
            context['form'].initial.update([('purchaser_company', purchaser_company)])
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, company_creator=request.user.company)
        position_form = self.position_form(request.POST)
        set_correct_queryset_for_currency(position_form, request)
        if form.is_valid() and position_form.is_valid():
            new_note = form.save(commit=False)
            new_position = position_form.save()
            assign_fields_for_new_note(new_note, new_position, request)
            new_note.save()
            return HttpResponseRedirect(reverse_lazy('preview', kwargs={'pk': new_note.pk}))
        return render(request, 'debit_note/note_create.html', {'form': form, 'position_form': position_form})


class DebitNoteUpdateView(CompanyCreatorPermissionMixin, UpdateView):
    model = DebitNote
    template_name = 'debit_note/note_update.html'
    form_class = DebitNoteCreateForm
    position_formset = PositionInlineFormset

    def get(self, request, *args, **kwargs):
        debit_note = self.get_object()
        context = dict()
        context['form'] = self.form_class(instance=debit_note, company_creator=request.user.company)
        formset = self.position_formset(instance=debit_note)
        set_correct_queryset_for_currency(formset, request)
        context['formset'] = formset
        context['object'] = self.get_object()

        return render(request, 'debit_note/note_update.html', context)

    def post(self, request, *args, **kwargs):
        debit_note = self.get_object()
        pk = self.kwargs.get('pk')
        form = DebitNoteCreateForm(request.POST, company_creator=request.user.company, instance=debit_note)
        formset = self.position_formset(request.POST, instance=debit_note)
        set_correct_queryset_for_currency(formset, request)
        if form.is_valid() and formset.is_valid():
            formset.save()
            form.save()
            return HttpResponseRedirect(reverse('preview', kwargs={'pk': pk}))
        return render(request, 'debit_note/note_update.html', {'formset': formset, 'form': form, 'object': self.get_object()})


class DebitNoteDetailView(CompanyCreatorPermissionMixin, DetailView):
    model = DebitNote
    template_name = 'debit_note/note_preview.html'
    context_object_name = 'note'
    object = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['paid'] = self.get_object().is_paid
        return context

    def get(self, request, *args, **kwargs):
        payment_status = request.GET.get('paid')
        note = self.get_object()
        if payment_status == 'False':
            note.is_paid = False
        if payment_status == 'True':
            note.is_paid = True
        note.save()
        return render(request, self.template_name, self.get_context_data(note=note))


class DebitNoteListView(DebitNoteFilterMixin, ListView):
    model = DebitNote
    template_name = 'debit_note/note_list.html'
    context_object_name = 'notes'
    paginate_by = 10

    def get_queryset(self):
        return DebitNote.objects.filter(company_creator=self.request.user.company)\
            .annotate(positions_count=Count('positions'))\
            .filter(positions_count__gte=1)\


class DebitNoteDeleteView(CompanyCreatorPermissionMixin, DeleteView):
    model = DebitNote
    success_url = reverse_lazy('note_all')


class IssuerCompanyCreateView(CreateView):
    model = IssuerCompany
    form_class = IssuerCompanyCreateForm
    template_name = 'debit_note/issuer_create.html'
    success_url = reverse_lazy('issuer_list')
    address_form = AddressCreateForm

    def get(self, request, *args, **kwargs):
        context = {'form': self.form_class(initial={'company_creator': request.user.company}), 'address_form': self.address_form}
        if not IssuerCompany.objects.filter(tax_id=self.request.user.company.tax_id).exists():
            context['main_company_as_issuer_not_exists'] = True
            context['main_company_tax_id'] = self.request.user.company.tax_id
            context['main_company_name'] = self.request.user.company.name
        layout = {'tax_id': request.GET.get('tax_id')}
        if layout['tax_id']:
            layout_company = MainCompany.objects.get(tax_id=layout['tax_id'])
            context['form'] = self.form_class(initial={'company_creator': request.user.company}, instance=layout_company)
            context['address_form'] = self.address_form(instance=layout_company.address)
        return render(request, 'debit_note/issuer_create.html', context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        address_form = self.address_form(request.POST)
        context = {'form': form, 'address_form': address_form}
        if all((form.is_valid(), address_form.is_valid())):
            new_company = form.save(commit=False)
            new_address = address_form.save()
            new_company.address = new_address
            new_company.company_creator = request.user.company
            new_company.save()
            return HttpResponseRedirect(reverse_lazy('issuer_all'))
        return render(request, 'debit_note/issuer_create.html', context)


class IssuerCompanyUpdateView(CompanyCreatorPermissionMixin, UpdateView):
    model = IssuerCompany
    form_class = IssuerCompanyUpdateForm
    template_name = 'debit_note/issuer_update.html'
    success_url = reverse_lazy('issuer_all')
    address_form = AddressCreateForm

    def get_context_data(self, **kwargs):
        company = self.get_object()
        context = super().get_context_data()
        context['address_form'] = self.address_form(instance=company.address)
        return context

    def post(self, request, *args, **kwargs):
        company = self.get_object()
        form = self.form_class(request.POST, instance=company)
        address_form = self.address_form(request.POST, instance=company.address)
        context = {'form': form, 'address_form': address_form}
        print(form)
        pk = self.kwargs.get('pk')
        if form.is_valid() and address_form.is_valid():
            print('valid')
            address_form.save()
            company.save()
            return redirect('issuer_detail', pk)
        return render(request, 'debit_note/issuer_update.html', context)


class IssuerCompanyDetailView(CompanyCreatorPermissionMixin, DetailView):
    model = IssuerCompany
    template_name = 'debit_note/issuer_detail.html'
    pk_url_kwarg = 'pk'
    context_object_name = 'issuer'


class IssuerCompanyListView(ListView):
    template_name = 'debit_note/issuer_list.html'
    context_object_name = 'issuers'

    def get_queryset(self):
        return IssuerCompany.objects.filter(company_creator=self.request.user.company)


class IssuerCompanyDeleteView(CompanyCreatorPermissionMixin, DeleteView):
    model = IssuerCompany
    success_url = reverse_lazy('issuer_all')


class BankAccountCreateView(CompanyCreatorPermissionMixin, CreateView):
    model = IssuerCompany
    template_name = 'debit_note/bank_account_create.html'
    form_class = BankAccountCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['issuer'] = self.get_object()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            new_bank_account = form.save(commit=False)
            owner_company = self.get_object()
            new_bank_account.owner = owner_company
            new_bank_account.save()
            return HttpResponseRedirect(reverse('issuer_detail', kwargs={'pk': self.kwargs.get('pk')}))
        return render(request, 'debit_note/bank_account_create.html')


class BankAccountUpdateView(CompanyCreatorPermissionMixin, UpdateView):
    model = BankAccount
    form_class = BankAccountCreateForm
    template_name = 'debit_note/bank_account_update.html'
    pk_url_kwarg = 'account_pk'

    def test_func(self):
        if self.get_object().owner.company_creator == self.request.user.company:
            return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['issuer'] = IssuerCompany.objects.get(pk=self.kwargs.get('pk'))
        context['form'] = self.form_class(instance=self.get_object())
        context['account_pk'] = self.kwargs['account_pk']
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, instance=self.get_object())
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('issuer_detail', kwargs={'pk': self.kwargs.get('pk')}))
        return render(request, 'debit_note/bank_account_update.html')


class BankAccountDeleteView(CompanyCreatorPermissionMixin, DeleteView):
    model = BankAccount
    pk_url_kwarg = 'account_pk'

    def test_func(self):
        if self.get_object().owner.company_creator == self.request.user.company:
            return HttpResponseForbidden()

    def delete(self, request, *args, **kwargs):
        object = self.get_object()
        object.delete()
        return HttpResponseRedirect(reverse('issuer_detail', kwargs={'pk': self.kwargs.get('pk')}))


class PurchaserCompanyCreateView(CreateView):
    model = PurchaserCompany
    template_name = 'debit_note/purchaser_create.html'
    form_class = PurchaserCompanyCreateForm
    address_form = AddressCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['form'] = self.form_class(initial={'company_creator': self.request.user.company})
        context['address_form'] = self.address_form()
        if self.request.GET.get('tax_id'):
            request_tax_id = self.request.GET.get('tax_id')
            context['tax_id'] = request_tax_id
            if PurchaserCompany.objects.filter(tax_id=request_tax_id, company_creator=self.request.user.company).exists():
                purchaser_in_db = PurchaserCompany.objects.filter(tax_id=request_tax_id, company_creator=self.request.user.company).first()
                context['purchaser_in_db'] = purchaser_in_db
            else:
                try:
                    new_purchaser_api_request = CompanyDetailsFromAPIRequest(request_tax_id)
                    new_company_form_initial_data, new_address_form_initial_data = \
                        new_purchaser_api_request.prepare_initial_data_for_company_and_address_forms()
                    context['form'].initial.update(new_company_form_initial_data)
                    context['address_form'].initial.update(new_address_form_initial_data)
                except ConnectionError:
                    context['api_connection_error'] = True
        if self.request.GET.get('next'):
            context['next'] = self.request.GET.get('next')
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        address_form = self.address_form(request.POST)
        context = dict()
        context['form'] = form
        context['address_form'] = address_form
        if form.is_valid() and address_form.is_valid():
            new_company = form.save(commit=False)
            new_address = address_form.save()
            new_company.address = new_address
            new_company.company_creator = request.user.company
            new_company.save()
            next_link = {'url_name': request.GET.get('next')}
            if next_link.get('url_name'):
                return redirect(reverse(next_link.get('url_name')) + f'?tax_id={new_company.tax_id}')
            return redirect('purchaser_detail', new_company.pk)
        return render(request, 'debit_note/purchaser_create.html', context)


class PurchaserCompanyUpdateView(CompanyCreatorPermissionMixin, UpdateView):
    model = PurchaserCompany
    template_name = 'debit_note/purchaser_update.html'
    form_class = PurchaserCompanyUpdateForm
    address_form = AddressCreateForm

    def get_context_data(self, **kwargs):
        company = self.get_object()
        context = super().get_context_data()
        context['address_form'] = self.address_form(instance=company.address)
        return context

    def post(self, request, *args, **kwargs):
        company = self.get_object()
        form = self.form_class(request.POST, instance=company)
        address_form = self.address_form(request.POST, instance=company.address)
        context = {'company_form': form, 'address_form': address_form}
        pk = self.kwargs.get('pk')
        if form.is_valid() and address_form.is_valid():
            address_form.save()
            company.save()
            return redirect('purchaser_detail', pk)
        return render(request, 'debit_note/purchaser_update.html', context)


class PurchaserCompanyDetailView(CompanyCreatorPermissionMixin, DebitNoteFilterMixin, DetailView):
    model = PurchaserCompany
    template_name = 'debit_note/purchaser_detail.html'
    context_object_name = 'purchaser'

    def filter_get_queryset(self):
        queryset = DebitNote.objects.filter(company_creator=self.request.user.company, purchaser_company=self.kwargs['pk'])
        queries = list()
        if self.request.GET.get('year'):
            queries.append(Q(issue_date__year__in=self.request.GET.getlist('year')))
        if self.request.GET.get('month'):
            queries.append(Q(issue_date__month__in=self.request.GET.getlist('month')))
        if self.request.GET.get('is_paid'):
            queries.append(Q(is_paid__in=self.request.GET.getlist('is_paid')))
        for query in queries:
            queryset = queryset.filter(query)
        return queryset


class PurchaserCompanyListView(ListView):
    template_name = 'debit_note/purchasers_list.html'
    context_object_name = 'purchasers'

    def get_queryset(self):
        return PurchaserCompany.objects.filter(company_creator=self.request.user.company)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        if self.request.GET.get('tax_id'):
            search_tax_id = self.request.GET.get('tax_id').strip()
            context['tax_id'] = search_tax_id
            if PurchaserCompany.objects.filter(tax_id=search_tax_id, company_creator=self.request.user.company).exists():
                context['search_purchaser'] = PurchaserCompany.objects.get(tax_id=search_tax_id)
        return context


class PurchaserCompanyDeleteView(CompanyCreatorPermissionMixin, DeleteView):
    model = PurchaserCompany
    success_url = reverse_lazy('purchaser_all')


def download_note_in_pdf(request, pk):
    try:
        path_to_pdf_file = convert_html_to_pdf('debit_note/note_for_print_and_pdf.html', pk, request)
        return FileResponse(open(path_to_pdf_file, 'rb'), as_attachment=True)
    except:
        pass
    finally:
        remove_html_and_pdf_files(path_to_pdf_file.split('.')[0])


class DebitNoteShowHTMLForPrintView(CompanyCreatorPermissionMixin, DetailView):
    model = DebitNote
    context_object_name = 'note'
    template_name = 'debit_note/note_for_print_and_pdf.html'


class DebitNoteSettingsView(DebitNoteSettingsMixin, View):
    pass


def create_purchaser_companies_json_response(request):
    tax_id_param = request.GET.get('tax_id')
    company_creator_param = request.GET.get('company_creator')
    companies = purchaser_search_ajax_handling(tax_id_param, company_creator_param)
    return JsonResponse({'queryset': companies})
