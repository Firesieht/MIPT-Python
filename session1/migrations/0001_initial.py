# Generated by Django 5.0.3 on 2024-03-13 13:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FileUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('Пространство', 'Пространство'), ('Экспонат', 'Экспонат'), ('Студия', 'Студия'), ('Преподаватель', 'Преподаватель')], max_length=200, verbose_name='Тип файла')),
                ('file', models.FileField(upload_to='', verbose_name='Файл')),
            ],
        ),
        migrations.CreateModel(
            name='Prostranstvo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Наименование')),
                ('volume', models.PositiveIntegerField(verbose_name='Вместимость')),
                ('description', models.TextField(verbose_name='Описание')),
            ],
        ),
        migrations.CreateModel(
            name='Studio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Наименование')),
                ('description', models.TextField(verbose_name='Описание')),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=300, verbose_name='ФИО')),
            ],
        ),
        migrations.CreateModel(
            name='ProstrSutdioMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prostr', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='session1.prostranstvo')),
                ('studio', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='session1.studio')),
            ],
        ),
        migrations.CreateModel(
            name='Exhibits',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Наименование')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='session1.prostrsutdiomapping', verbose_name='Владелец')),
            ],
        ),
    ]
