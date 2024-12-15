# Generated by Django 5.0.3 on 2024-03-14 08:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('session1', '0004_eventtype_location_prostranstvo_location_event_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='prostranstvo',
            old_name='location',
            new_name='loc',
        ),
        migrations.AddField(
            model_name='location',
            name='space',
            field=models.ManyToManyField(to='session1.prostranstvo', verbose_name='Места'),
        ),
        migrations.RemoveField(
            model_name='event',
            name='spaces',
        ),
        migrations.AlterField(
            model_name='eventmoneyrelation',
            name='space',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='session1.location', verbose_name='Пространство'),
        ),
        migrations.AddField(
            model_name='event',
            name='spaces',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='session1.prostranstvo', verbose_name='Количество'),
        ),
    ]
