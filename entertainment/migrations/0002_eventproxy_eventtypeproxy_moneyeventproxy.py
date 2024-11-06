# Generated by Django 5.0.3 on 2024-03-14 07:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entertainment', '0001_initial'),
        ('session1', '0004_eventtype_location_prostranstvo_location_event_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventProxy',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('session1.event',),
        ),
        migrations.CreateModel(
            name='EventTypeProxy',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('session1.event',),
        ),
        migrations.CreateModel(
            name='MoneyEventProxy',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('session1.moneyevent',),
        ),
    ]
