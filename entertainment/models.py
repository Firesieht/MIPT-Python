from django.db import models
from session1.models import Prostranstvo, Event, MoneyEvent, EventType, Location

class ProstranstvoProxy(Prostranstvo):
    class Meta:
        proxy = True
        verbose_name = 'Пространство'
        verbose_name_plural = 'Пространства'


class EventProxy(Event):
    class Meta:
        proxy = True
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'


class EventTypeProxy(EventType):
    class Meta:
        proxy = True
        verbose_name = 'Тип мероприятия'
        verbose_name_plural = 'Типы меропритий'


class MoneyEventProxy(MoneyEvent):
    class Meta:
        proxy = True
        verbose_name = 'Установка цен на билеты'
        verbose_name_plural = 'Установка цен на билеты'


class LocationProxy(Location):
    class Meta:
        proxy = True
        verbose_name = 'Локация'
        verbose_name_plural = 'Локации'
