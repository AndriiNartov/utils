# Generated by Django 3.2.7 on 2022-04-16 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='letter',
            name='comment',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Comment'),
        ),
        migrations.AlterField(
            model_name='letter',
            name='status_date',
            field=models.DateField(default=models.DateField(verbose_name='Date of sending'), verbose_name='Date of last status changing'),
        ),
    ]
