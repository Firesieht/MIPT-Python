# Generated by Django 5.0.3 on 2024-03-14 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('session3', '0004_report_reportrow'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='report',
            name='description',
        ),
        migrations.AddField(
            model_name='reportrow',
            name='description',
            field=models.CharField(max_length=300, null=True, verbose_name='Описание'),
        ),
    ]
