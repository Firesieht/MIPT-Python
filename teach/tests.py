from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import (
    Studio, Teacher, StudioWorkReport, Day, Visitors,
    ReportToVisitStudio, ReportCenterState, AbonimentSale,
    CostAbonimentsCreateion
)
from django.utils import timezone
from datetime import date, time


class StudioWorkReportModelTest(TestCase):
    def setUp(self):
        self.studio = Studio.objects.create(name="Студия Танцев")
        self.teacher = Teacher.objects.create(name="Иван Иванов")
        self.day_monday = Day.objects.create(name="Понедельник")
        self.day_wednesday = Day.objects.create(name="Среда")

    def test_str_method(self):
        report = StudioWorkReport.objects.create(
            date_created=timezone.now(),
            studio=self.studio,
            teacher=self.teacher,
            date_studio_work_start=date.today(),
            date_studio_work_end=date.today(),
            time_start=time(10, 0),
            time_end=time(18, 0)
        )
        report.work_days.set([self.day_monday, self.day_wednesday])
        self.assertEqual(
            str(report),
            f'Приказ о работе студий ({report.date_created}, {self.teacher})'
        )

    def test_clean_time_validation(self):
        report = StudioWorkReport(
            date_created=timezone.now(),
            studio=self.studio,
            teacher=self.teacher,
            date_studio_work_start=date.today(),
            date_studio_work_end=date.today(),
            time_start=time(18, 0),
            time_end=time(10, 0)
        )
        report.work_days.set([self.day_monday])
        with self.assertRaises(ValidationError) as context:
            report.clean()
        self.assertIn('Время начала не может быть больше Времени конца', str(context.exception))

    def test_clean_teacher_busy_validation(self):
        StudioWorkReport.objects.create(
            date_created=timezone.now(),
            studio=self.studio,
            teacher=self.teacher,
            date_studio_work_start=date.today(),
            date_studio_work_end=date.today(),
            time_start=time(10, 0),
            time_end=time(12, 0)
        )
        overlapping_report = StudioWorkReport(
            date_created=timezone.now(),
            studio=self.studio,
            teacher=self.teacher,
            date_studio_work_start=date.today(),
            date_studio_work_end=date.today(),
            time_start=time(11, 0),
            time_end=time(13, 0)
        )
        overlapping_report.work_days.set([self.day_monday])
        with self.assertRaises(ValidationError) as context:
            overlapping_report.clean()
        self.assertIn('Учитель занят в это время', str(context.exception))


class CostAbonimentsCreateionModelTest(TestCase):
    def setUp(self):
        self.studio = Studio.objects.create(name="Студия Йоги")
        self.teacher = Teacher.objects.create(name="Мария Петрова")
        self.report = StudioWorkReport.objects.create(
            date_created=timezone.now(),
            studio=self.studio,
            teacher=self.teacher,
            date_studio_work_start=date.today(),
            date_studio_work_end=date.today(),
            time_start=time(9, 0),
            time_end=time(17, 0)
        )

    def test_cost_calculation_on_creation(self):
        cost_creation = CostAbonimentsCreateion.objects.create(
            report=self.report,
            one_type=1000
        )
        expected_month = 1000 * 2 * 4
        expected_month -= expected_month * 0.06  # 6% скидка
        expected_year = 1000 * 2 * 4 * 9
        expected_year -= expected_year * 0.16  # 16% скидка
        self.assertAlmostEqual(cost_creation.month_type, expected_month)
        self.assertAlmostEqual(cost_creation.year_type, expected_year)


class AbonimentSaleModelTest(TestCase):
    def setUp(self):
        self.studio = Studio.objects.create(name="Студия Фитнеса")
        self.teacher = Teacher.objects.create(name="Алексей Смирнов")
        self.report = StudioWorkReport.objects.create(
            date_created=timezone.now(),
            studio=self.studio,
            teacher=self.teacher,
            date_studio_work_start=date.today(),
            date_studio_work_end=date.today(),
            time_start=time(8, 0),
            time_end=time(20, 0)
        )
        self.visitor = Visitors.objects.create(visitor="Елена Кузнецова")
        self.cost_creation = CostAbonimentsCreateion.objects.create(
            report=self.report,
            one_type=1500
        )

    def test_aboniment_sale_creation(self):
        visit_report = ReportToVisitStudio.objects.create(
            date_created=date.today(),
            working_report=self.report,
            visitor=self.visitor
        )
        sale = AbonimentSale.objects.create(
            report_visitor=visit_report,
            aboniment_type='Месячный'
        )
        sale.refresh_from_db()
        self.assertEqual(sale.report_studio, self.report)
        self.assertEqual(sale.visitor, self.visitor)
        self.assertEqual(sale.cost, self.cost_creation.month_type)


class SignalTests(TestCase):
    def setUp(self):
        self.studio = Studio.objects.create(name="Студия Художественная")
    
    def test_post_save_studioproxy_creates_exhibit_owner_proxy(self):
        # Предполагается, что ExhibitOwnerProxy имеет поле studio
        from session1.models import ExhibitOwnerProxy
        StudioProxy.objects.create(name="Студия Художественная")
        self.assertTrue(ExhibitOwnerProxy.objects.filter(studio=self.studio).exists())

    def test_post_save_aboniment_sale_updates_cost(self):
        teacher = Teacher.objects.create(name="Сергей Иванов")
        report = StudioWorkReport.objects.create(
            date_created=timezone.now(),
            studio=self.studio,
            teacher=teacher,
            date_studio_work_start=date.today(),
            date_studio_work_end=date.today(),
            time_start=time(10, 0),
            time_end=time(18, 0)
        )
        cost_creation = CostAbonimentsCreateion.objects.create(
            report=report,
            one_type=2000
        )
        visitor = Visitors.objects.create(visitor="Анна Сергеевна")
        visit_report = ReportToVisitStudio.objects.create(
            date_created=date.today(),
            working_report=report,
            visitor=visitor
        )
        sale = AbonimentSale.objects.create(
            report_visitor=visit_report,
            aboniment_type='Годовой'
        )
        sale.refresh_from_db()
        self.assertEqual(sale.cost, cost_creation.year_type)
        self.assertEqual(sale.report_studio, report)
        self.assertEqual(sale.visitor, visitor)
