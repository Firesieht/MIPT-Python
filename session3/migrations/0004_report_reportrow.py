# Generated by Django 5.0.3 on 2024-03-14 10:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('session1', '0006_alter_event_spaces_alter_moneyevent_event_and_more'),
        ('session3', '0003_alter_ticket_cost'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_started', models.DateField(verbose_name='Дата начала')),
                ('date_end', models.DateField(verbose_name='Дата конца')),
                ('description', models.CharField(max_length=300, verbose_name='Описание')),
            ],
        ),
        migrations.CreateModel(
            name='ReportRow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField(verbose_name='Количество проданных билетов')),
                ('cost', models.PositiveIntegerField(verbose_name='Их стоимость')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='session1.event', verbose_name='Мероприятие')),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='session3.report', verbose_name='Отчет')),
            ],
        ),
    ]
