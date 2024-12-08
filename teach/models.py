from django.db import models
from session1.models import Studio, Teacher, ExhibitOwnerProxy
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.db.models import Q


class StudioProxy(Studio):
    """
    Прокси-модель для Студий.

    Позволяет управлять студиями в админ-панели.
    """
    class Meta:
        proxy=True
        verbose_name = 'Студия'
        verbose_name_plural = 'Студии'


class TeacherProxy(Teacher):
    """
    Прокси-модель для Учителей.

    Используется для управления учителями в админ-панели.
    """
    class Meta:
        proxy=True
        verbose_name = 'Учитель'
        verbose_name_plural = 'Учителя'


class Day(models.Model):
    """
    Модель для хранения дней недели.

    Атрибуты:
        name (CharField): Название дня недели.
    """
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
        """
        Строковое представление дня.

        Возвращает название дня недели.
        """
        return self.name


class StudioWorkReport(models.Model):
    """
    Модель для хранения информации о работе студий.

    Атрибуты:
        date_created (DateTimeField): Дата формирования приказа.
        studio (ForeignKey): Связь со студией.
        teacher (ForeignKey): Связь с учителем.
        work_days (ManyToManyField): Рабочие дни.
        date_studio_work_start (DateField): Дата начала работы студии.
        date_studio_work_end (DateField): Дата окончания работы студии.
        time_start (TimeField): Время начала работы студии.
        time_end (TimeField): Время окончания работы студии.
    """
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
        """
        Валидация информации о работе студии.

        Проверяет, что время окончания не раньше времени начала и что преподаватель не занят в указанное время.
        """
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
        """
        Строковое представление приказа о работе студии.

        Возвращает строку с датой создания и именем учителя.
        """
        return f'Приказ о работе студий ({self.date_created}, {self.teacher})'


class TimeTableTeacher(models.Model):
    """
    Модель для хранения расписания работы учителя.

    Атрибуты:
        date_start (DateField): Дата начала отчетного периода.
        date_end (DateField): Дата окончания отчетного периода.
        teacher (ForeignKey): Связь с учителем.
    """
    date_start = models.DateField('Дата начала отчета')
    date_end = models.DateField('Дата окончания отчета')
    teacher = models.ForeignKey(Teacher, verbose_name='Преподаватель', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'График работы преподавателя (Отчет)'
        verbose_name_plural = 'Графики работ преподавателей (Отчеты)'
    
    def __str__(self):
        """
        Строковое представление расписания учителя.

        Возвращает строку с именем учителя и периодом отчета.
        """
        return f'График работы преподавателя {self.teacher} в период {self.date_start} - {self.date_end}'


class TableCellTeacher(models.Model):
    """
    Модель для хранения информации о строках расписания учителя.

    Атрибуты:
        days (CharField): Рабочие дни недели.
        timing (CharField): Время занятий.
        studio (ForeignKey): Связь со студией.
        timetable (ForeignKey): Связь с расписанием.
    """
    days = models.CharField('Рабочие дни недели', max_length=200)
    timing = models.CharField("Время занятий", max_length=200)
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE, verbose_name='Студия')
    timetable = models.ForeignKey(TimeTableTeacher, verbose_name='Таблица', on_delete=models.CASCADE)

    def __str__(self):
        """
        Строковое представление строки расписания учителя.

        Возвращает строку 'Строка отчета'.
        """
        return f'Строка отчета'

    class Meta:
        verbose_name = 'Строка отчета'
        verbose_name_plural = 'Строки отчета'


class Visitors(models.Model):
    """
    Модель для хранения информации о посетителях центра.

    Атрибуты:
        visitor (CharField): ФИО посетителя.
    """
    visitor = models.CharField('ФИО посетителя', max_length=200)

    class Meta:
        verbose_name = 'Посетитель центра'
        verbose_name_plural = 'Посетители центра'
    
    def __str__(self):
        """
        Строковое представление посетителя.

        Возвращает строку с именем посетителя.
        """
        return f'Посетитель центра {self.visitor}'


class ReportToVisitStudio(models.Model):
    """
    Модель для хранения заявок на посещение студии.

    Атрибуты:
        date_created (DateField): Дата заявки.
        working_report (ForeignKey): Связь с приказом о работе студии.
        visitor (ForeignKey): Связь с посетителем.
    """
    date_created = models.DateField('Дата заявки')
    working_report = models.ForeignKey(StudioWorkReport, verbose_name='Приказ о работе студии', on_delete=models.CASCADE)
    visitor = models.ForeignKey(Visitors, verbose_name='Посетитель', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Заявка на посещение студии'
        verbose_name_plural = 'Заявки на посещения студий'
    
    def __str__(self):
        """
        Строковое представление заявки.

        Возвращает строку с именем посетителя и студией.
        """
        return f'Заявка на посещение студии {self.visitor}, студия: {self.working_report.studio}'


class ReportCenterState(models.Model):
    """
    Модель для хранения общего отчета о работе культурного центра.

    Атрибуты:
        date_start (DateField): Дата начала отчетного периода.
        date_end (DateField): Дата окончания отчетного периода.
    """
    date_start = models.DateField('Дата начала')
    date_end = models.DateField('Дата окончания')

    def __str__(self):
        """
        Строковое представление отчета центра.

        Возвращает строку с периодом отчета.
        """
        return f'Отчет о работе культурного центра {self.date_start} - {self.date_end}'

    class Meta:
        verbose_name = 'Отчет о работе культурного центра'
        verbose_name_plural = 'Отчеты о работах культурных центров'


class ReportStudentMapping(models.Model):
    """
    Модель для сопоставления студентов с отчетами центра.

    Атрибуты:
        visitors (TextField): Участники.
        studio (ForeignKey): Связь со студией.
        report (ForeignKey): Связь с общим отчетом.
    """
    visitors = models.TextField(verbose_name='Участники', null=True)
    studio = models.ForeignKey(Studio, verbose_name='Студия', on_delete=models.CASCADE, null=True)
    # visitor = models.ForeignKey(Visitors, verbose_name='Участник', on_delete=models.CASCADE)
    report = models.ForeignKey(ReportCenterState, verbose_name='Отчет', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Участники'
        verbose_name_plural = 'Участники'
    
    def __str__(self):
        """
        Строковое представление сопоставления студентов.

        Возвращает строку 'Отчет'.
        """
        return f'Отчет'


class CostAbonimentsCreateion(models.Model):
    """
    Модель для установки цен на абонементы.

    Атрибуты:
        date_created (DateTimeField): Дата установки цен.
        report (ForeignKey): Связь с приказом о работе студии.
        one_type (PositiveIntegerField): Цена разового абонемента.
        month_type (PositiveIntegerField): Цена месячного абонемента.
        year_type (PositiveIntegerField): Цена годового абонемента.
    """
    date_created = models.DateTimeField('Дата установки цен', auto_now_add=True)
    report = models.ForeignKey(StudioWorkReport, verbose_name='Приказ о работе студии', on_delete=models.CASCADE)

    one_type = models.PositiveIntegerField('Единоразовый абонимент')
    month_type = models.PositiveIntegerField('Месячный абонимент', null=True, blank=True)
    year_type = models.PositiveIntegerField('Годовой абонимент', null=True, blank=True)

    class Meta:
        verbose_name = 'Установка цены на абонемент'
        verbose_name_plural = 'Установка цен на абонемент'
    
    def __str__(self):
        """
        Строковое представление установки цен на абонементы.

        Возвращает строку с информацией о связанном приказе.
        """
        return f'Установка цен на: {self.report}'


class AbonimentSale(models.Model):
    """
    Модель для хранения информации о продаже абонементов.

    Атрибуты:
        date_sell (DateField): Дата продажи абонемента.
        report_studio (ForeignKey): Связь с приказом о работе студии.
        report_visitor (ForeignKey): Связь с заявкой на посещение студии.
        visitor (ForeignKey): Связь с посетителем.
        aboniment_type (CharField): Тип абонемента.
        cost (PositiveIntegerField): Стоимость абонемента.
    """
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
        """
        Строковое представление продажи абонемента.

        Возвращает строку с информацией о продаже абонемента.
        """
        return f'Продажа абонимента {self.report_studio}'


class AbonimentSaleReport(models.Model):
    """
    Модель для хранения отчетов о продажах абонементов.

    Атрибуты:
        total_sum (PositiveIntegerField): Итоговая сумма продаж.
        date_started (DateField): Дата начала отчетного периода.
        date_end (DateField): Дата окончания отчетного периода.
        studios (ManyToManyField): Связь с студиями.
    """
    total_sum = models.PositiveIntegerField('Итоговая сумма продаж', null=True)
    date_started = models.DateField('Дата начала')
    date_end = models.DateField('Дата окончания')
    studios = models.ManyToManyField(Studio, verbose_name='Студии')

    class Meta:
        verbose_name = 'Отчет о продажах абонементов'
        verbose_name_plural = 'Отчеты о продажах абониментов'
    
    def __str__(self):
        """
        Строковое представление отчета о продажах абонементов.

        Возвращает строку с общей суммой продаж.
        """
        return f'Отчет о продаже абонементов на {self.total_sum}'


class AbonimentReportMapping(models.Model):
    """
    Модель для сопоставления информации об абонементах со студиями в отчетах.

    Атрибуты:
        studio (ForeignKey): Связь со студией.
        aboniments_info (TextField): Информация об абонементах.
        total_sum (PositiveIntegerField): Итоговая сумма.
        report (ForeignKey): Связь с отчетом.
    """
    studio = models.ForeignKey(Studio, verbose_name='Студия', on_delete=models.CASCADE)
    aboniments_info = models.TextField('Информация об абониментах', null=True)
    total_sum = models.PositiveIntegerField('Итоговая сумма')
    report = models.ForeignKey(AbonimentSaleReport, on_delete=models.CASCADE, verbose_name='Отчет', null=True)

    class Meta:
        verbose_name = 'Информация о студии по абониментам'
        verbose_name_plural = 'Информации о студиях по абониментам'
    
    def __str__(self):
        """
        Строковое представление сопоставления информации об абонементах.

        Возвращает строку с информацией о студии.
        """
        return f'Информация о студии: {self.studio}'


@receiver(post_save, sender=StudioProxy)
def organization(sender, instance, *args, **kwargs):
    """
    Сигнал для создания ExhibitOwnerProxy при сохранении StudioProxy.

    Args:
        sender: Отправитель сигнала.
        instance (StudioProxy): Экземпляр студии.
        *args: Дополнительные аргументы.
        **kwargs: Дополнительные аргументы.
    """
    ExhibitOwnerProxy.objects.create(studio=instance)


@receiver(post_save, sender=TimeTableTeacher)
def teacher_create(sender, instance, created, **kwargs):
    """
    Сигнал для создания строк расписания учителя при создании расписания.

    При создании нового расписания для учителя генерируются строки расписания для соответствующих студий.
    
    Args:
        sender: Отправитель сигнала.
        instance (TimeTableTeacher): Экземпляр расписания.
        created (bool): Флаг создания.
        **kwargs: Дополнительные аргументы.
    """
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
    """
    Сигнал для создания сопоставлений студентов в отчете центра при его создании.

    Собирает информацию о посетителях, которые посетили студии в отчетном периоде, и создает соответствующие записи.
    
    Args:
        sender: Отправитель сигнала.
        instance (ReportCenterState): Экземпляр отчета центра.
        created (bool): Флаг создания.
        **kwargs: Дополнительные аргументы.
    """
    if created:
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
    """
    Сигнал для автоматического расчета цен на абонементы при их создании.

    При создании нового объекта установки цен рассчитываются цены на месячный и годовой абонементы.
    
    Args:
        sender: Отправитель сигнала.
        instance (CostAbonimentsCreateion): Экземпляр установки цен.
        created (bool): Флаг создания.
        **kwargs: Дополнительные аргументы.
    """
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
    """
    Сигнал для установки стоимости абонемента при его продаже.

    При создании новой продажи абонемента автоматически устанавливается его стоимость на основе типа абонемента.
    
    Args:
        sender: Отправитель сигнала.
        instance (AbonimentSale): Экземпляр продажи абонемента.
        created (bool): Флаг создания.
        **kwargs: Дополнительные аргументы.
    """
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
    """
    Сигнал для обновления отчета о продажах абонементов при изменении связанных студий.

    Собирает данные о продажах абонементов для выбранных студий и обновляет общий отчет.
    
    Args:
        sender: Отправитель сигнала.
        instance (AbonimentSaleReport): Экземпляр отчета о продажах абонементов.
        **kwargs: Дополнительные аргументы.
    """
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
Годовые абонементы: {report[cell][0][2]} раз куплено на сумму {report[cell][1][2]} рублей
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