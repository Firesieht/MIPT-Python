# Generated by Django 5.0.3 on 2024-03-14 07:55

import django.db.models.deletion
import django.db.models.fields.related
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('session1', '0003_alter_studio_name_alter_teacher_full_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название мероприятия')),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('Партер', 'Партер'), ('Амфитеатр', 'Амфитеатр'), ('Балкон', 'Балкон')], max_length=100, verbose_name='Тип локации')),
                ('amount', models.PositiveIntegerField(default=1, verbose_name='Мест в ряду')),
                ('row', models.PositiveIntegerField(default=1, verbose_name='Рядов')),
            ],
        ),
        migrations.AddField(
            model_name='prostranstvo',
            name='location',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='Дата проведения')),
                ('name', models.CharField(max_length=200, verbose_name='Название')),
                ('time_started', models.TimeField(verbose_name='Время начала')),
                ('time_end', models.TimeField(verbose_name='Время окончания')),
                ('users_amount', models.PositiveIntegerField(verbose_name='Количество поситителей')),
                ('is_money', models.BooleanField(default=False, verbose_name='Платно?')),
                ('description', models.TextField(default='', verbose_name='Описание')),
                ('spaces', models.ManyToManyField(related_name='Количество', to='session1.prostranstvo')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='session1.eventtype', verbose_name='Тип мероприятия')),
            ],
        ),
        migrations.CreateModel(
            name='MoneyEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='session1.event')),
            ],
        ),
        migrations.CreateModel(
            name='EventMoneyRelation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cost', models.PositiveIntegerField(verbose_name='Цена за место')),
                ('space', models.ForeignKey(on_delete=django.db.models.fields.related.ForeignKey, to='session1.location', verbose_name='Пространство')),
                ('money_event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='session1.moneyevent')),
            ],
        ),
    ]