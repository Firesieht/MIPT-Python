from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Report, ReportRow, Sale, BareSell, Ticket, TicketAvailable, TicketRow
from session1.models import Event, Location, EventMoneyRelation
from django.utils import timezone
from datetime import date, timedelta

class ReportModelTest(TestCase):
    def setUp(self):
        self.report = Report(
            date_started=date.today(),
            date_end=date.today() + timedelta(days=7)
        )

    def test_report_clean_valid_dates(self):
        try:
            self.report.clean()
        except ValidationError:
            self.fail("Report.clean() raised ValidationError unexpectedly!")

    def test_report_clean_invalid_dates(self):
        self.report.date_end = self.report.date_started - timedelta(days=1)
        with self.assertRaises(ValidationError):
            self.report.clean()

    def test_report_str(self):
        expected_str = f'Отчет ({self.report.date_started} - {self.report.date_end})'
        self.assertEqual(str(self.report), expected_str)

class SaleModelTest(TestCase):
    def setUp(self):
        self.event = Event.objects.create(name="Test Event", is_money=True)
        self.sale = Sale(event=self.event)

    def test_sale_clean_valid_event(self):
        try:
            self.sale.clean()
        except ValidationError:
            self.fail("Sale.clean() raised ValidationError unexpectedly!")

    def test_sale_clean_invalid_event(self):
        self.event.is_money = False
        self.event.save()
        with self.assertRaises(ValidationError):
            self.sale.clean()

    def test_sale_str(self):
        self.sale.save()
        expected_str = f'Продажа {self.event.name}, {self.sale.date_sell}'
        self.assertEqual(str(self.sale), expected_str)

class BareSellModelTest(TestCase):
    def setUp(self):
        self.event = Event.objects.create(name="Test Event", is_money=True)
        self.sale = Sale.objects.create(event=self.event)
        self.bare_sell = BareSell(sell=self.sale, money=50)

    def test_bare_sell_clean_valid(self):
        # Assuming spaces.volume is greater than current sold tickets
        self.event.spaces.volume = 100
        self.event.spaces.save()
        try:
            self.bare_sell.clean()
        except ValidationError:
            self.fail("BareSell.clean() raised ValidationError unexpectedly!")

    def test_bare_sell_clean_invalid(self):
        self.event.spaces.volume = 1
        self.event.spaces.save()
        BareSell.objects.create(sell=self.sale, money=1)
        with self.assertRaises(ValidationError):
            self.bare_sell.clean()

    def test_bare_sell_str(self):
        self.bare_sell.save()
        self.assertEqual(str(self.bare_sell), '')
