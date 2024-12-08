from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import (
    Location, EventType, Prostranstvo, Event, MoneyEvent,
    EventMoneyRelation, Studio, ProstrSutdioMapping, Teacher,
    Exhibition, Organization, ExhibitOwnerProxy, Exhibits, FileUpload
)
from django.utils import timezone
from datetime import date, time


class LocationModelTest(TestCase):
    def setUp(self):
        self.prostranstvo = Prostranstvo.objects.create(
            name="Main Hall",
            volume=100
        )
        self.location = Location.objects.create(
            type="Партер",
            amount=10,
            row=5
        )
        self.location.space.add(self.prostranstvo)

    def test_suply_property(self):
        self.assertEqual(self.location.suply, 50)

    def test_str_method(self):
        expected_str = 'Партер (50 мест; 5 рядов, 10 мест в ряде, пространства: Main Hall)'
        self.assertEqual(str(self.location), expected_str)


class EventTypeModelTest(TestCase):
    def test_str_method(self):
        event_type = EventType.objects.create(name="Концерт")
        self.assertEqual(str(event_type), "Концерт")


class ProstranstvoModelTest(TestCase):
    def setUp(self):
        self.prostranstvo = Prostranstvo.objects.create(
            name="Main Hall",
            volume=100,
            description="Главный зал",
            loc=True
        )
        self.location1 = Location.objects.create(
            type="Партер",
            amount=10,
            row=5
        )
        self.location2 = Location.objects.create(
            type="Балкон",
            amount=5,
            row=4
        )
        self.prostranstvo.space.add(self.location1, self.location2)

    def test_clean_method_valid(self):
        try:
            self.prostranstvo.clean()
        except ValidationError:
            self.fail("Prostranstvo.clean() raised ValidationError unexpectedly!")

    def test_clean_method_invalid_volume(self):
        self.prostranstvo.volume = 40  # Less than total suply (50 + 20)
        with self.assertRaises(ValidationError):
            self.prostranstvo.clean()

    def test_str_method(self):
        expected_str = 'Main Hall'
        self.assertEqual(str(self.prostranstvo), expected_str)


class EventModelTest(TestCase):
    def setUp(self):
        self.event_type = EventType.objects.create(name="Концерт")
        self.prostranstvo = Prostranstvo.objects.create(
            name="Main Hall",
            volume=100,
            description="Главный зал",
            loc=False
        )
        self.event = Event.objects.create(
            date=date.today(),
            name="Rock Night",
            type=self.event_type,
            time_started=time(18, 0),
            time_end=time(21, 0),
            users_amount=80,
            spaces=self.prostranstvo,
            is_money=True,
            description="Вечер рок-музыки"
        )

    def test_clean_method_valid(self):
        try:
            self.event.clean()
        except ValidationError:
            self.fail("Event.clean() raised ValidationError unexpectedly!")

    def test_clean_method_invalid_volume(self):
        self.event.users_amount = 120  # Exceeds volume
        with self.assertRaises(ValidationError):
            self.event.clean()

    def test_clean_method_invalid_time(self):
        self.event.time_started = time(22, 0)
        self.event.time_end = time(21, 0)
        with self.assertRaises(ValidationError):
            self.event.clean()

    def test_str_method(self):
        expected_str = 'Rock Night(Платное, Пространство: Main Hall)'
        self.assertEqual(str(self.event), expected_str)


class MoneyEventModelTest(TestCase):
    def setUp(self):
        self.event_type = EventType.objects.create(name="Концерт")
        self.prostranstvo = Prostranstvo.objects.create(
            name="Main Hall",
            volume=100,
            description="Главный зал",
            loc=False
        )
        self.event = Event.objects.create(
            date=date.today(),
            name="Rock Night",
            type=self.event_type,
            time_started=time(18, 0),
            time_end=time(21, 0),
            users_amount=80,
            spaces=self.prostranstvo,
            is_money=True,
            description="Вечер рок-музыки"
        )
        self.money_event = MoneyEvent.objects.create(event=self.event)

    def test_str_method(self):
        expected_str = f'Установка цен на {str(self.event)}'
        self.assertEqual(str(self.money_event), expected_str)

    def test_clean_method_non_money_event(self):
        self.money_event.event.is_money = False
        self.money_event.event.save()
        with self.assertRaises(ValidationError):
            self.money_event.clean()


class StudioModelTest(TestCase):
    def test_upload_excel(self):
        data = ["Studio A", "Описание студии А"]
        Studio.upload_excel(data)
        self.assertTrue(Studio.objects.filter(name="Studio A").exists())

    def test_str_method(self):
        studio = Studio.objects.create(name="Studio A", description="Описание студии А")
        self.assertEqual(str(studio), "Studio A")


class OrganizationModelTest(TestCase):
    def test_str_method(self):
        organization = Organization.objects.create(name="Org A")
        self.assertEqual(str(organization), "Org A")


class ExhibitsModelTest(TestCase):
    def setUp(self):
        self.studio = Studio.objects.create(name="Studio A", description="Описание студии А")
        self.exhibit_owner = ExhibitOwnerProxy.objects.create(studio=self.studio)
    
    def test_upload_excel(self):
        data = ["Exhibit A", "Studio A"]
        Exhibits.upload_excel(data)
        self.assertTrue(Exhibits.objects.filter(name="Exhibit A", owner=self.exhibit_owner).exists())
    
    def test_str_method(self):
        exhibit = Exhibits.objects.create(name="Exhibit A", owner=self.exhibit_owner)
        self.assertEqual(str(exhibit), "Exhibit A")


class FileUploadModelTest(TestCase):
    def test_str_method(self):
        file_upload = FileUpload.objects.create(type="Пространство", file="path/to/file.xlsx")
        expected_str = 'Загрузка файлов (Пространство)'
        self.assertEqual(str(file_upload), expected_str)


class SignalsTest(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name="Org A")
        self.studio = Studio.objects.create(name="Studio A", description="Описание студии А")

    def test_organization_signal(self):
        proxy = ExhibitOwnerProxy.objects.get(org=self.organization)
        self.assertEqual(proxy.org, self.organization)

    def test_studio_signal(self):
        proxy = ExhibitOwnerProxy.objects.get(studio=self.studio)
        self.assertEqual(proxy.studio, self.studio)
