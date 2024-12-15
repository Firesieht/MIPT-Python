# Generated by Django 5.0.3 on 2024-03-14 13:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('session3', '0006_alter_report_options_alter_sale_options_baresell'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='baresell',
            options={'verbose_name': 'Обычная продажа', 'verbose_name_plural': 'Обычные продажи'},
        ),
        migrations.AlterModelOptions(
            name='reportrow',
            options={'verbose_name': 'Объект отчета', 'verbose_name_plural': 'Объекты отчета'},
        ),
        migrations.AlterModelOptions(
            name='ticket',
            options={'verbose_name': 'Билет', 'verbose_name_plural': 'Билеты'},
        ),
        migrations.AlterModelOptions(
            name='ticketavailable',
            options={'verbose_name': 'Доступность билетов', 'verbose_name_plural': 'Доступности билетова'},
        ),
        migrations.AlterModelOptions(
            name='ticketrow',
            options={'verbose_name': 'Ряд билетов', 'verbose_name_plural': 'Ряды билетов'},
        ),
    ]
