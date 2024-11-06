# Generated by Django 5.0.3 on 2024-03-14 10:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entertainment', '0002_eventproxy_eventtypeproxy_moneyeventproxy'),
        ('session1', '0006_alter_event_spaces_alter_moneyevent_event_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocationProxy',
            fields=[
            ],
            options={
                'verbose_name': 'Локация',
                'verbose_name_plural': 'Локации',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('session1.location',),
        ),
        migrations.AlterModelOptions(
            name='eventproxy',
            options={'verbose_name': 'Мероприятие', 'verbose_name_plural': 'Мероприятия'},
        ),
        migrations.AlterModelOptions(
            name='eventtypeproxy',
            options={'verbose_name': 'Тип мероприятия', 'verbose_name_plural': 'Типы меропритий'},
        ),
        migrations.AlterModelOptions(
            name='moneyeventproxy',
            options={'verbose_name': 'Установка цен на билеты', 'verbose_name_plural': 'Установка цен на билеты'},
        ),
    ]
