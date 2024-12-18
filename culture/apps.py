from django.apps import AppConfig


class CultureConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'culture'
    verbose_name = 'Культурно-просветительская деятельность (выставки, лекции)'
    verbose_name_plural = 'Культурно-просветительская деятельность (выставки, лекции)'
