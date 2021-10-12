# Generated by Django 3.2.7 on 2021-09-21 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('debit_note', '0002_auto_20210921_1310'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='issuercompany',
            constraint=models.UniqueConstraint(fields=('tax_id', 'company_creator'), name='unique_issuer'),
        ),
        migrations.AddConstraint(
            model_name='purchasercompany',
            constraint=models.UniqueConstraint(fields=('tax_id', 'company_creator'), name='unique_purchaser'),
        ),
    ]
