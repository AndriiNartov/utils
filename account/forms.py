from django import forms
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.forms import modelformset_factory


from .models import User, MainCompany, Address


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'


class RegisterUserForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput,
        help_text=password_validation.password_validators_help_text_html()
    )
    password2 = forms.CharField(
        label='Пароль(повторно)',
        widget=forms.PasswordInput,
        help_text='Введите тот же пароль для проверки'
    )
    first_name = forms.CharField(
        label='Имя'
    )
    last_name = forms.CharField(
        label='Фамилия'
    )

    def clean_password1(self):
        password1 = self.cleaned_data['password1']
        if password1:
            password_validation.validate_password(password1)
        return password1

    def clean(self):
        super().clean()
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 and password2 and password1 != password2:
            errors = {'password2': ValidationError('Введённые пароли не совпадают', code='password_mismatch')}
            raise ValidationError(errors)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.username = f'{self.cleaned_data["last_name"]}{self.cleaned_data["first_name"]}'
        user.save()
        return user

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'password1', 'password2')


class AddressCreateForm(forms.ModelForm):

    class Meta:
        model = Address
        fields = '__all__'


class MainCompanyCreateForm(forms.ModelForm):

    class Meta:
        model = MainCompany
        fields = ('name', 'phone', 'tax_id')


UnconfirmedUsersFormset = modelformset_factory(
    User,
    fields=('username', 'is_confirmed_by_admin',),
    widgets={
            'is_confirmed_by_admin': forms.CheckboxInput(attrs={'id': 'is_confirmed_by_admin'})
        },
    extra=0,
)


class GroupCreateForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple, queryset=Permission.objects.all())

    class Meta:
        model = Group
        fields = ('name', 'permissions')


class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        exclude = ('password', 'is_superuser', 'user_permissions', 'last_login', 'is_staff', 'company')