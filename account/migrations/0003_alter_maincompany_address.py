# Generated by Django 3.2.7 on 2021-09-22 13:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_auto_20210921_1310'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maincompany',
            name='address',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='account.address'),
        ),
    ]
