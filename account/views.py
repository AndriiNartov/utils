from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView
from django.views.generic.base import ContextMixin

from .models import User, MainCompany
from .forms import AddressCreateForm, MainCompanyCreateForm, RegisterUserForm


class RegisterUserView(CreateView):
    model = User
    template_name = 'account/register_user.html'
    form_class = RegisterUserForm
    success_url = reverse_lazy('login')

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.is_confirmed_by_admin = True
            new_user.save()
            return HttpResponseRedirect(reverse_lazy('login'))
        return render(request, 'account/register_user.html', {'form': form})


class RegisterUserByInvitationView(RegisterUserView):

    def get(self, request, *args, **kwargs):
        invitation_link_suffix = self.kwargs['invitation_link']
        if not MainCompany.objects.filter(invitation_link_suffix=invitation_link_suffix).exists():
            return HttpResponse('Ваша ссылка некорректна. Обратитесь к Вашему администратору!')
        return render(request, 'account/register_user.html', {'form': self.form_class()})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            invitation_link_suffix = self.kwargs['invitation_link']
            try:
                company = MainCompany.objects.get(invitation_link_suffix=invitation_link_suffix)
                new_user.company = company
                new_user.is_active = False
                new_user.save()
                return HttpResponseRedirect(reverse_lazy('login'))
            except:
                return HttpResponse('Ваша ссылка некорректна. Обратитесь к Вашему администратору!')
        return render(request, 'account/register_user.html', {'form': form})


class MainCompanyCreateView(CreateView):
    model = MainCompany
    template_name = 'account/create_company.html'
    form_class = MainCompanyCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['address_form'] = AddressCreateForm()
        return context

    def get(self, *args, **kwargs):
        if self.request.user.company:
            messages.add_message(self.request, messages.INFO, f'Вы уже зарегистрированы в компании "{self.request.user.company}"')
            return redirect('company_detail', self.request.user.company.pk)
        return super().get(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        address_form = AddressCreateForm(request.POST)
        user = request.user
        if form.is_valid() and address_form.is_valid():
            new_address = address_form.save()
            new_company = form.save(commit=False)
            new_company.address = new_address
            new_company.save()
            user.company = new_company
            user.is_company_admin = True
            user.save()
            return HttpResponseRedirect(reverse_lazy('company_detail', kwargs={'pk': new_company.pk}))
        return render(request, 'account/create_company.html', {
            'form': form,
            'address_form': address_form
        })


class MainCompanyDetailView(DetailView):
    model = MainCompany
    pk_url_kwarg = 'pk'
    context_object_name = 'company'
    template_name = 'account/company_detail.html'


class LoginUserView(LoginView):
    template_name = 'account/login.html'


class MainCompanyManageView(ContextMixin, View):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = self.request.user.company
        context['company'] = company
        context['active_users'] = User.objects.filter(
            company=company,
            is_confirmed_by_admin=True
        )
        context['not_confirmed_users'] = User.objects.filter(
            company=company,
            is_confirmed_by_admin=False
        )
        return context

    def get(self, *args, **kwargs):
        if not self.request.user.is_company_admin:
            return HttpResponseForbidden()
        return render(self.request, 'account/company_manage.html', self.get_context_data())
