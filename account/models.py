import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


def change_duplicated_username(username):
    last_object_with_similar_username = User.objects.filter(username__startswith=username).last()
    last_char_of_username = last_object_with_similar_username.username[-1]
    try:
        number_of_last_object_with_similar_username = int(last_char_of_username)
        new_username = f'{username}{number_of_last_object_with_similar_username + 1}'
        return new_username
    except:
        new_username = f'{username}1'
        return new_username


class User(AbstractUser):
    company = models.ForeignKey(
        'MainCompany',
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='employees',
        verbose_name='Компания'
    )
    is_company_admin = models.BooleanField(default=False, blank=True, null=True, verbose_name='Админ')
    is_confirmed_by_admin = models.BooleanField(default=False, blank=True, null=True, verbose_name='Подтверждён админом')

    def save(self, *args, **kwargs):
        if User.objects.filter(username__startswith=self.username).exists():
            last_existing_user = User.objects.filter(username__startswith=self.username).last()
            if not self.pk == last_existing_user.pk:
                self.username = change_duplicated_username(self.username)
        super().save()


class Company(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название фирмы')
    tax_id = models.CharField(max_length=50, verbose_name='Налоговый номер', unique=True)
    address = models.ForeignKey('account.Address', on_delete=models.SET_NULL, null=True)
    phone = models.CharField(max_length=50, verbose_name='Номер телефона', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class MainCompany(Company):
    invitation_link_suffix = models.UUIDField(
        default=uuid.uuid4,
        verbose_name='Суффикс для ссылки-приглашения',
        blank=True,
        null=True,
        editable=False
    )

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'


class Address(models.Model):
    zip_code = models.CharField(max_length=15, verbose_name='Код города')
    city_name = models.CharField(max_length=50, verbose_name='Название города')
    street_name = models.CharField(max_length=50, verbose_name='Название улицы')
    house_number = models.CharField(max_length=20, verbose_name='Номер дома и квартиры')

    def __str__(self):
        return f'{self.zip_code} {self.city_name}, {self.street_name} {self.house_number}'
