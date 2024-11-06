from django.db import models
from session1.models import Studio, Teacher, ExhibitOwnerProxy
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.db.models import Q


class StudioProxy(Studio):
    class Meta:
        proxy=True
        verbose_name = 'Студия'
        verbose_name_plural = 'Студии'


class TeacherProxy(Teacher):
    class Meta:
        proxy=True
        verbose_name = 'Учитель'
        verbose_name_plural = 'Учителя'


class Day(models.Model):
    name = models.CharField(choices=[
        ('Понедельник', 'Понедельник'),
        ('Вторник', 'Вторник'),
        ('Среда', 'Среда'),
        ('Четверг', 'Четверг'),
        ('Пятница', 'Пятница'),
        ('Суббота', 'Суббота'),
        ('Воскресенье', 'Воскресенье')
    ], max_length=200)

    class Meta:
        verbose_name = 'День'
        verbose_name_plural = 'Дни'
    
    def __str__(self):
        return self.name


class StudioWorkReport(models.Model):
    date_created = models.DateTimeField('Дата формирования приказа')
    studio = models.ForeignKey(Studio, verbose_name='Студия', on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, verbose_name='Преподаватель', on_delete=models.CASCADE)
    work_days = models.ManyToManyField(Day, verbose_name='Рабочие дни')
    date_studio_work_start = models.DateField('Дата начала работы студии')
    date_studio_work_end = models.DateField('Дата окончания работы студии')
    time_start = models.TimeField('Время начала работы студии')
    time_end = models.TimeField('Дата окончания работы студии')

    class Meta:
        verbose_name = 'Приказ о работе студий'
        verbose_name_plural = 'Приказы о работах студий'
    
    def clean(self):
        if self.time_end < self.time_start:
            raise ValidationError('Время начала не может быть больше Времени конца')
        q1 = set(map(lambda x: x.id, StudioWorkReport.objects.filter(teacher=self.teacher).exclude(
            Q(time_start__gte=self.time_end) | Q(time_end__lte=self.time_start) 
        )))
        q2 = set(map(lambda x: x.id, StudioWorkReport.objects.filter(teacher=self.teacher).exclude(
            Q(date_studio_work_start__gte=self.date_studio_work_end) | Q(date_studio_work_end__lte=self.date_studio_work_start)
        )))
        q3 = q1 & q2
        try:
            q3.remove(self.id)
        except: pass
        if len(q3):
            raise ValidationError('Учитель занят в это время')
    
    def __str__(self):
        return f'Приказ о работе студий ({self.date_created}, {self.teacher})'


class TimeTableTeacher(models.Model):
    date_start = models.DateField('Дата начала отчета')
    date_end = models.DateField('Дата окончания отчета')
    teacher = models.ForeignKey(Teacher, verbose_name='Преподаватель', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'График работы преподавателя (Отчет)'
        verbose_name_plural = 'Графики работ преподавателей (Отчеты)'
    
    def __str__(self):
        return f'График работы преподавателя {self.teacher} в период {self.date_start} - {self.date_end}'

class TableCellTeacher(models.Model):
    days = models.CharField('Рабочие дни недели', max_length=200)
    timing = models.CharField("Время занятий", max_length=200)
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE, verbose_name='Студия')
    timetable = models.ForeignKey(TimeTableTeacher, verbose_name='Таблица', on_delete=models.CASCADE)

    def __str__(self):
        return f'Строка отчета'

    class Meta:
        verbose_name = 'Строка отчета'
        verbose_name = 'Строки отчета'

class Visitors(models.Model):
    visitor = models.CharField('ФИО посетителя', max_length=200)

    class Meta:
        verbose_name = 'Посетитель центра'
        verbose_name_plural = 'Посетители центра'
    
    def __str__(self):
        return f'Посететитель центра {self.visitor}'


class ReportToVisitStudio(models.Model):
    date_created = models.DateField('Дата заявки')
    working_report = models.ForeignKey(StudioWorkReport, verbose_name='Приказ о работе студии', on_delete=models.CASCADE)
    visitor = models.ForeignKey(Visitors, verbose_name='Посетитель', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Заявка на посещение студии'
        verbose_name_plural = 'Заявки на посещения студий'
    
    def __str__(self):
        return f'Заявка на посещение студии {self.visitor}, студия: {self.working_report.studio}'


class ReportCenterState(models.Model):
    date_start = models.DateField('Дата начала')
    date_end = models.DateField('Дата окончания')

    def __str__(self):
        return f'Отчет о работе культурного центра {self.date_start} - {self.date_end}'

    class Meta:
        verbose_name = 'Отчет о работе культурного центра'
        verbose_name_plural = 'Отчеты о работах культурных центров'


class ReportStudentMapping(models.Model):
    visitors = models.TextField(verbose_name='Участники', null=True)
    studio = models.ForeignKey(Studio, verbose_name='Студия', on_delete=models.CASCADE, null=True)
    # visitor = models.ForeignKey(Visitors, verbose_name='Участник', on_delete=models.CASCADE)
    report = models.ForeignKey(ReportCenterState, verbose_name='Отчет', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Участники'
        verbose_name_plural = 'Участники'
    
    def __str__(self):
        return f'Отчет'


class CostAbonimentsCreateion(models.Model):
    date_created = models.DateTimeField('Дата установки цен', auto_now_add=True)
    report = models.ForeignKey(StudioWorkReport, verbose_name='Приказ о работе студии', on_delete=models.CASCADE)

    one_type = models.PositiveIntegerField('Единоразовый абонимент')
    month_type = models.PositiveIntegerField('Месячный абонимент', null=True, blank=True)
    year_type = models.PositiveIntegerField('Годовой абонимент', null=True, blank=True)

    class Meta:
        verbose_name = 'Установка цены на абонемент'
        verbose_name_plural = 'Установка цен на абонемент'
    
    
    def __str__(self):
        return f'Установка цен на: {self.report}'


class AbonimentSale(models.Model):
    date_sell = models.DateField('Дата продажи абонмента')
    report_studio = models.ForeignKey(StudioWorkReport, verbose_name='Приказ о работе студии', on_delete=models.CASCADE, null=True, blank=True)
    report_visitor = models.ForeignKey(ReportToVisitStudio, verbose_name='Заявка на посещение студии', on_delete=models.CASCADE, null=True)
    visitor = models.ForeignKey(Visitors, on_delete=models.CASCADE, verbose_name='Студент', null=True, blank=True)
    aboniment_type = models.CharField(
        choices=[
            ('Разовый', 'Разовый'),
            ('Месячный', 'Месячный'),
            ('Годовой', 'Годовой')
        ],
        max_length=200,
        verbose_name = 'Тип абонимента'
    )
    cost = models.PositiveIntegerField('Цена', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Продажа абониментов'
        verbose_name_plural = 'Продажи абониментов'
    
    def __str__(self):
        return f'Прадажа абонимента {self.report_studio}'

    

class AbonimentSaleReport(models.Model):
    total_sum = models.PositiveIntegerField('Итоговая сумма продаж', null=True)
    date_started = models.DateField('Дата начала')
    date_end = models.DateField('Дата окончания')
    studios = models.ManyToManyField(Studio, verbose_name='Студии')

    class Meta:
        verbose_name = 'Отчет о продажах абонементов'
        verbose_name_plural = 'Отчеты о продажах абониментов'
    
    def __str__(self):
        return f'Отчет о продажи абонементов на {self.total_sum}'


class AbonimentReportMapping(models.Model):
    studio = models.ForeignKey(Studio, verbose_name='Студия', on_delete=models.CASCADE)
    aboniments_info = models.TextField('Информация об абониментах')
    total_sum = models.PositiveIntegerField('Итоговая сумма')
    report = models.ForeignKey(AbonimentSaleReport, on_delete=models.CASCADE, verbose_name='Отчет', null=True)

    class Meta:
        verbose_name = 'Информация о студии по абониментам'
        verbose_name_plural = 'Информации о студиях по абониментам'
    
    def __str__(self):
        return f'Информация о студии: {self.studio}'


@receiver(post_save, sender=StudioProxy)
def organization(sender, instance, *args, **kwargs):
    ExhibitOwnerProxy.objects.create(studio=instance)


@receiver(post_save, sender=TimeTableTeacher)
def teacher_create(sender, instance, created, **kwargs):
    if created:
        for studio_report in StudioWorkReport.objects.filter(teacher=instance.teacher, date_studio_work_start__lte=instance.date_end, date_studio_work_end__gte=instance.date_start):
            time_start = max(instance.date_start, studio_report.date_studio_work_start)
            time_end = min(instance.date_end, studio_report.date_studio_work_end)
            days = ''
            for day in studio_report.work_days.all():
                days += f'{day.name} '
            TableCellTeacher.objects.create(
                days=days,
                timing=f'От {time_start} до {time_end} Во время {studio_report.time_start} - {studio_report.time_end} ',
                studio=studio_report.studio,
                timetable=instance
            )

@receiver(post_save, sender=ReportCenterState)
def report_create(sender, instance, created, **kwargs):
    studios = dict()
    for visit_report in ReportToVisitStudio.objects.filter(date_created__gte=instance.date_start):
        if not visit_report.working_report.studio.id in studios.keys():
            studios.update({visit_report.working_report.studio.id: ''})
        studios[visit_report.working_report.studio.id] += f'{visit_report.visitor} '
    
    for studio in studios.keys():
        ReportStudentMapping.objects.create(
            visitors=studios[studio],
            studio=Studio.objects.get(id=studio),
            report=instance
        )

@receiver(post_save, sender=CostAbonimentsCreateion)
def calculate_cost(sender, instance, created, **kwargs):
    if created:
        one_cost = instance.one_type
        month_cost = one_cost * 2 * 4
        month_cost -= month_cost * 0.06

        year_cost = one_cost * 2 * 4 * 9
        year_cost -= year_cost * 0.16

        instance.month_type = month_cost
        instance.year_type = year_cost
        instance.save()

@receiver(post_save, sender=AbonimentSale)
def aboniment_sale(sender, instance: AbonimentSale, created, **kwargs):
    if created:
        rep = instance.report_visitor.working_report
        visitor = instance.report_visitor.visitor
        instance.report_studio = rep
        instance.visitor = visitor
        costs = CostAbonimentsCreateion.objects.filter(report=instance.report_studio).order_by('-date_created').first()
        if instance.aboniment_type == 'Разовый':
            instance.cost = costs.one_type
        elif instance.aboniment_type == 'Месячный':
            instance.cost = costs.month_type
        else:
            instance.cost = costs.year_type
        instance.save()

@receiver(m2m_changed, sender=AbonimentSaleReport.studios.through)
def aboniment_sale_report(sender, instance: AbonimentSaleReport, **kwargs):
    total = 0
    stds = list(map(lambda x: x.id, instance.studios.all()))
    report = dict()
    AbonimentReportMapping.objects.filter(report=instance).delete()
    for studio in stds:
        report.update({studio: [[0, 0, 0], [0, 0, 0]]})
    for sale in AbonimentSale.objects.filter(
        date_sell__gte=instance.date_started, 
        date_sell__lte=instance.date_end, 
        report_studio__studio__id__in=stds
    ):
        studio_id = sale.report_studio.studio.id
        if studio_id not in report.keys():
            report.update({studio_id: [[0,0,0], [0,0,0]]})
        if sale.aboniment_type == 'Разовый':
            report[studio_id][0][0] += 1
            report[studio_id][1][0] += sale.cost
        elif sale.aboniment_type == 'Месячный':
            report[studio_id][0][1] += 1
            report[studio_id][1][1] += sale.cost
        else:
            report[studio_id][0][2] += 1
            report[studio_id][1][2] += sale.cost
    for cell in report.keys():
        info_str = f'''Разовые абонименты: {report[cell][0][0]} раз куплено на сумму {report[cell][1][0]} рублей
Месячные абонементы: {report[cell][0][1]} раз куплено на сумму {report[cell][1][1]} рублей
Годовые абонементы: {report[cell][0][2]} раз куплено на сумму {report[cell][1][2]} рубелй
        '''
        local_total = report[cell][1][0] + report[cell][1][1] + report[cell][1][2]
        total += local_total
        AbonimentReportMapping.objects.create(
            studio=Studio.objects.get(id=cell),
            aboniments_info=info_str,
            total_sum=local_total,
            report=instance
        )
    instance.total_sum = total
    instance.save()

# @receiver(post_save, sender=AbonimentSale)
# def sale_auto(sender, instance: AbonimentSale,created, **kwargs):
#     if created:
#         rep = instance.report_visitor.working_report
#         visitor = instance.report_visitor.visitor
#         instance.report_studio = rep
#         instance.visitor = visitor
#         instance.save()