from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import (
    OrganizationProxy,
    ExhibitProxy,
    ExhibitionProxy,
    OrderToCreateExhibition,
    OrderExhibitionFromAuthors,
    OrderExhibitionToExhibit,
    OrderToReturn,
    ExhibitAuthorMapping
)
from session1.models import Prostranstvo, Exhibits, Exhibition

class OrganizationProxyTests(TestCase):
    def setUp(self):
        self.organization = OrganizationProxy.objects.create(name="Тестовая Организация")

    def test_str_representation(self):
        self.assertEqual(str(self.organization), "Тестовая Организация")

class ExhibitProxyTests(TestCase):
    def setUp(self):
        self.exhibit = Exhibits.objects.create(name="Тестовый Экспонат")
        self.exhibit_proxy = ExhibitProxy.objects.get(id=self.exhibit.id)

    def test_proxy_behavior(self):
        self.assertIsInstance(self.exhibit_proxy, ExhibitProxy)

    def test_str_representation(self):
        self.assertEqual(str(self.exhibit_proxy), "Тестовый Экспонат")

class ExhibitionProxyTests(TestCase):
    def setUp(self):
        self.exhibition = Exhibition.objects.create(name="Тестовая Выставка", ex_type="Внутренняя")
        self.exhibition_proxy = ExhibitionProxy.objects.get(id=self.exhibition.id)

    def test_proxy_behavior(self):
        self.assertIsInstance(self.exhibition_proxy, ExhibitionProxy)

    def test_str_representation(self):
        self.assertEqual(str(self.exhibition_proxy), "Тестовая Выставка")

class OrderToCreateExhibitionTests(TestCase):
    def setUp(self):
        self.prostranstvo = Prostranstvo.objects.create(name="Тестовое Пространство")
        self.exhibition = Exhibition.objects.create(name="Тестовая Выставка", ex_type="Внутренняя")
        self.order = OrderToCreateExhibition.objects.create(
            date_created=timezone.now(),
            exhibition=self.exhibition,
            date_start=timezone.now(),
            date_end=timezone.now(),
            place=self.prostranstvo
        )

    def test_str_representation(self):
        expected_str = f'Приказ о проведении ({self.order.date_created}, {self.exhibition})'
        self.assertEqual(str(self.order), expected_str)

class OrderExhibitionFromAuthorsTests(TestCase):
    def setUp(self):
        self.prostranstvo = Prostranstvo.objects.create(name="Тестовое Пространство")
        self.exhibition = Exhibition.objects.create(name="Внешняя Выставка", ex_type="Внешняя")
        self.order_create = OrderToCreateExhibition.objects.create(
            date_created=timezone.now(),
            exhibition=self.exhibition,
            date_start=timezone.now(),
            date_end=timezone.now(),
            place=self.prostranstvo
        )
        self.order_from_authors = OrderExhibitionFromAuthors.objects.create(
            date_getting=timezone.now(),
            creation_order=self.order_create
        )

    def test_str_representation(self):
        expected_str = f'Приказ о получении экспонатов: {self.order_create}'
        self.assertEqual(str(self.order_from_authors), expected_str)

    def test_clean_valid_exhibition_type(self):
        try:
            self.order_from_authors.clean()
        except ValidationError:
            self.fail("clean() raised ValidationError unexpectedly!")

    def test_clean_invalid_exhibition_type(self):
        self.exhibition.ex_type = "Внутренняя"
        self.exhibition.save()
        with self.assertRaises(ValidationError):
            self.order_from_authors.clean()

class OrderExhibitionToExhibitTests(TestCase):
    def setUp(self):
        self.prostranstvo = Prostranstvo.objects.create(name="Тестовое Пространство")
        self.exhibition = Exhibition.objects.create(name="Тестовая Выставка", ex_type="Внутренняя")
        self.order_create = OrderToCreateExhibition.objects.create(
            date_created=timezone.now(),
            exhibition=self.exhibition,
            date_start=timezone.now(),
            date_end=timezone.now(),
            place=self.prostranstvo
        )
        self.order_to_exhibit = OrderExhibitionToExhibit.objects.create(
            date_to_provide=timezone.now(),
            order_to_create_exhibit=self.order_create
        )

    def test_str_representation(self):
        expected_str = f'Акт передачи экспонатов на выставку ({self.order_create})'
        self.assertEqual(str(self.order_to_exhibit), expected_str)

    def test_clean_exhibits_available(self):
        exhibit = Exhibits.objects.create(name="Экспонат 1")
        mapping = ExhibitAuthorMapping.objects.create(
            owner="Автор 1",
            exhibit=exhibit,
            order_to_create=self.order_create
        )
        try:
            self.order_to_exhibit.clean()
        except ValidationError:
            self.fail("clean() raised ValidationError unexpectedly!")

class OrderToReturnTests(TestCase):
    def setUp(self):
        self.prostranstvo = Prostranstvo.objects.create(name="Тестовое Пространство")
        self.exhibition = Exhibition.objects.create(name="Внешняя Выставка", ex_type="Внешняя")
        self.order_create = OrderToCreateExhibition.objects.create(
            date_created=timezone.now(),
            exhibition=self.exhibition,
            date_start=timezone.now(),
            date_end=timezone.now(),
            place=self.prostranstvo
        )
        self.order_return = OrderToReturn.objects.create(
            date_return=timezone.now(),
            order_to_create=self.order_create
        )

    def test_str_representation(self):
        expected_str = f'Акт возврата экспонатов: {self.order_create}'
        self.assertEqual(str(self.order_return), expected_str)

    def test_clean_with_author_mapping(self):
        ExhibitAuthorMapping.objects.create(
            owner="Автор 1",
            exhibit=Exhibits.objects.create(name="Экспонат 1"),
            order_to_create=self.order_create
        )
        try:
            self.order_return.clean()
        except ValidationError:
            self.fail("clean() raised ValidationError unexpectedly!")

    def test_clean_without_author_mapping(self):
        with self.assertRaises(ValidationError):
            self.order_return.clean()

class ExhibitAuthorMappingTests(TestCase):
    def setUp(self):
        self.exhibit = Exhibits.objects.create(name="Экспонат 1")
        self.exhibition = Exhibition.objects.create(name="Внешняя Выставка", ex_type="Внешняя")
        self.prostranstvo = Prostranstvo.objects.create(name="Тестовое Пространство")
        self.order_create = OrderToCreateExhibition.objects.create(
            date_created=timezone.now(),
            exhibition=self.exhibition,
            date_start=timezone.now(),
            date_end=timezone.now(),
            place=self.prostranstvo
        )

    def test_str_representation(self):
        mapping = ExhibitAuthorMapping.objects.create(
            owner="Автор 1",
            exhibit=self.exhibit,
            order_to_create=self.order_create
        )
        expected_str = "Маршрут"
        self.assertEqual(str(mapping), "Маршрут")

    def test_clean_external_exhibit_owner_valid(self):
        mapping = ExhibitAuthorMapping.objects.create(
            owner="Автор 1",
            exhibit=self.exhibit,
            order_to_create=self.order_create
        )
        try:
            mapping.clean()
        except ValidationError:
            self.fail("clean() raised ValidationError unexpectedly!")

    def test_clean_external_exhibit_owner_invalid(self):
        self.exhibition.ex_type = "Внутренняя"
        self.exhibition.save()
        mapping = ExhibitAuthorMapping.objects.create(
            owner="Автор 1",
            exhibit=self.exhibit,
            order_to_create=self.order_create
        )
        with self.assertRaises(ValidationError):
            mapping.clean()
