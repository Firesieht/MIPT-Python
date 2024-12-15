from django.db import models
from session1.models import Prostranstvo, Event, MoneyEvent, EventType, Location


class ProstranstvoProxy(Prostranstvo):
    """
    Прокси-модель для Пространств.

    Используется для управления пространствами в админ-панели.
    """
    class Meta:
        proxy = True
        verbose_name = 'Пространство'
        verbose_name_plural = 'Пространства'


class EventProxy(Event):
    """
    Прокси-модель для Мероприятий.

    Позволяет управлять мероприятиями в админ-панели.
    """
    class Meta:
        proxy = True
        verbose_name = 'Мероприятие'
        verbose_name_plural = 'Мероприятия'


class EventTypeProxy(EventType):
    """
    Прокси-модель для Типов Мероприятий.

    Используется для управления типами мероприятий в админ-панели.
    """
    class Meta:
        proxy = True
        verbose_name = 'Тип мероприятия'
        verbose_name_plural = 'Типы мероприятий'


class MoneyEventProxy(MoneyEvent):
    """
    Прокси-модель для Установки Цен на Билеты.

    Позволяет управлять установкой цен на билеты в админ-панели.
    """
    class Meta:
        proxy = True
        verbose_name = 'Установка цен на билеты'
        verbose_name_plural = 'Установка цен на билеты'


class LocationProxy(Location):
    """
    Прокси-модель для Локаций.

    Используется для управления локациями в админ-панели.
    """
    class Meta:
        proxy = True
        verbose_name = 'Локация'
        verbose_name_plural = 'Локации'
