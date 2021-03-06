# Generated by Django 3.2.7 on 2022-04-16 11:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Truck',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plate_number', models.CharField(max_length=15, unique=True, verbose_name='Plate number')),
            ],
        ),
        migrations.CreateModel(
            name='Letter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('track_number', models.CharField(default='b/n', max_length=30, unique=True, verbose_name='Track number')),
                ('sending_date', models.DateField(verbose_name='Date of sending')),
                ('status_date', models.DateField(verbose_name='Date of last status changing')),
                ('comment', models.CharField(blank=True, max_length=50, null=True, verbose_name='Status')),
                ('status', models.CharField(choices=[('OW', 'В пути'), ('DT', 'Передан на доставку'), ('NA', 'Авизо'), ('SD', 'Доставлено'), ('NT', 'Не бьётся')], default='OW', max_length=30, verbose_name='Status')),
                ('truck', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='letters', to='post.truck', verbose_name='Truck number')),
            ],
        ),
    ]
