from django.apps import AppConfig


class EntertainmentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'entertainment'
    verbose_name = 'Развлекательная деятельность (концерты, спектакли)'
    verbose_name_plural = 'Развлекательная деятельность (концерты, спектакли)'
