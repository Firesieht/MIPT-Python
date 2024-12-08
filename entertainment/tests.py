from django.test import TestCase
from session1.models import Prostranstvo, Event, EventType, MoneyEvent, Location
from .models import (
    ProstranstvoProxy,
    EventProxy,
    EventTypeProxy,
    MoneyEventProxy,
    LocationProxy
)

class ProstranstvoProxyTest(TestCase):
    def setUp(self):
        self.prostranstvo = ProstranstvoProxy.objects.create(
            name="Test Prostranstvo",
            description="Описание пространства"
        )

    def test_prostranstvo_creation(self):
        self.assertEqual(self.prostranstvo.name, "Test Prostranstvo")
        self.assertEqual(self.prostranstvo.description, "Описание пространства")
        self.assertTrue(isinstance(self.prostranstvo, Prostranstvo))

    def test_verbose_name(self):
        meta = ProstranstvoProxy._meta
        self.assertEqual(meta.verbose_name, "Пространство")
        self.assertEqual(meta.verbose_name_plural, "Пространства")


class EventProxyTest(TestCase):
    def setUp(self):
        event_type = EventTypeProxy.objects.create(name="Концерт")
        location = LocationProxy.objects.create(name="Стадион")
        self.event = EventProxy.objects.create(
            title="Тестовое мероприятие",
            event_type=event_type,
            location=location,
            date="2023-10-10"
        )

    def test_event_creation(self):
        self.assertEqual(self.event.title, "Тестовое мероприятие")
        self.assertEqual(self.event.event_type.name, "Концерт")
        self.assertEqual(self.event.location.name, "Стадион")
        self.assertTrue(isinstance(self.event, Event))

    def test_verbose_name(self):
        meta = EventProxy._meta
        self.assertEqual(meta.verbose_name, "Мероприятие")
        self.assertEqual(meta.verbose_name_plural, "Мероприятия")


class EventTypeProxyTest(TestCase):
    def setUp(self):
        self.event_type = EventTypeProxy.objects.create(name="Выставка")

    def test_event_type_creation(self):
        self.assertEqual(self.event_type.name, "Выставка")
        self.assertTrue(isinstance(self.event_type, EventType))

    def test_verbose_name(self):
        meta = EventTypeProxy._meta
        self.assertEqual(meta.verbose_name, "Тип мероприятия")
        self.assertEqual(meta.verbose_name_plural, "Типы мероприятий")


class MoneyEventProxyTest(TestCase):
    def setUp(self):
        self.money_event = MoneyEventProxy.objects.create(
            event_type="Билеты",
            price=100.00
        )

    def test_money_event_creation(self):
        self.assertEqual(self.money_event.event_type, "Билеты")
        self.assertEqual(self.money_event.price, 100.00)
        self.assertTrue(isinstance(self.money_event, MoneyEvent))

    def test_verbose_name(self):
        meta = MoneyEventProxy._meta
        self.assertEqual(meta.verbose_name, "Установка цен на билеты")
        self.assertEqual(meta.verbose_name_plural, "Установка цен на билеты")


class LocationProxyTest(TestCase):
    def setUp(self):
        self.location = LocationProxy.objects.create(name="Концертный зал")

    def test_location_creation(self):
        self.assertEqual(self.location.name, "Концертный зал")
        self.assertTrue(isinstance(self.location, Location))

    def test_verbose_name(self):
        meta = LocationProxy._meta
        self.assertEqual(meta.verbose_name, "Локация")
        self.assertEqual(meta.verbose_name_plural, "Локации")
