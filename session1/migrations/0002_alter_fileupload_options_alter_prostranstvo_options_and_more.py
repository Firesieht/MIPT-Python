# Generated by Django 5.0.3 on 2024-03-13 14:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('session1', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fileupload',
            options={'verbose_name': 'Загрузка файлов', 'verbose_name_plural': 'Загрузки файлов'},
        ),
        migrations.AlterModelOptions(
            name='prostranstvo',
            options={'verbose_name': 'Пространство', 'verbose_name_plural': 'Пространства'},
        ),
        migrations.AlterModelOptions(
            name='studio',
            options={'verbose_name': 'Студия', 'verbose_name_plural': 'Студии'},
        ),
        migrations.AlterField(
            model_name='exhibits',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='session1.studio', verbose_name='Владелец'),
        ),
        migrations.AlterField(
            model_name='prostranstvo',
            name='description',
            field=models.TextField(default='', verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='prostranstvo',
            name='volume',
            field=models.PositiveIntegerField(default=1, verbose_name='Вместимость'),
        ),
        migrations.AlterField(
            model_name='studio',
            name='description',
            field=models.TextField(default='', verbose_name='Описание'),
        ),
    ]