# Generated by Django 5.0.3 on 2024-03-15 11:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teach', '0009_alter_abonimentsalereport_total_sum'),
    ]

    operations = [
        migrations.AlterField(
            model_name='abonimentsale',
            name='visitor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='teach.visitors', verbose_name='Студент'),
        ),
    ]
