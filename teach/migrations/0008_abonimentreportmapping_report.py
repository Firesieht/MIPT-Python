# Generated by Django 5.0.3 on 2024-03-15 10:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teach', '0007_alter_abonimentsale_cost'),
    ]

    operations = [
        migrations.AddField(
            model_name='abonimentreportmapping',
            name='report',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='teach.abonimentsalereport', verbose_name='Отчет'),
        ),
    ]
