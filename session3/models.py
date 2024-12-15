from django.db import models
from session1.models import Event, Location, EventMoneyRelation
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError


class Report(models.Model):
    """
    Модель для создания отчетов о продажах билетов.

    Атрибуты:
        date_started (DateField): Дата начала отчетного периода.
        date_end (DateField): Дата окончания отчетного периода.
    """
    date_started = models.DateField('Дата начала')
    date_end = models.DateField('Дата конца')

    def clean(self):
        """
        Валидация дат отчетного периода.

        Проверяет, что дата окончания не раньше даты начала.
        """
        if self.date_end < self.date_started:
            raise ValidationError('Дата конца не может быть раньше даты начала')

    def __str__(self):
        """
        Строковое представление отчета.

        Возвращает строку с указанием периода отчета.
        """
        return f'Отчет ({self.date_started} - {self.date_end})'
    

    class Meta:
        verbose_name = 'Отчет'
        verbose_name_plural = 'Отчеты'


class ReportRow(models.Model):
    """
    Модель для хранения строк отчета о продажах билетов.

    Атрибуты:
        event (ForeignKey): Связь с мероприятием.
        amount (PositiveIntegerField): Количество проданных билетов.
        cost (PositiveIntegerField): Общая стоимость проданных билетов.
        report (ForeignKey): Связь с отчетом.
        description (CharField): Описание.
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name='Мероприятие')
    amount = models.PositiveIntegerField('Количество проданных билетов')
    cost = models.PositiveIntegerField('Их стоимость')
    report = models.ForeignKey(Report, on_delete=models.CASCADE, verbose_name='Отчет')
    description = models.CharField(max_length=300, verbose_name='Описание', null=True)

    def __str__(self):
        """
        Строковое представление строки отчета.

        Возвращает пустую строку.
        """
        return ''
    
    class Meta:
        verbose_name = 'Объект отчета'
        verbose_name_plural = 'Объекты отчета'


class Sale(models.Model):
    """
    Модель для хранения информации о продажах билетов.

    Атрибуты:
        date_sell (DateTimeField): Дата и время продажи.
        event (ForeignKey): Связь с мероприятием.
    """
    date_sell = models.DateTimeField('Дата продажи', auto_now_add=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name='Мероприятие')

    def clean(self):
        """
        Валидация продажи.

        Проверяет, что мероприятие является платным.
        """
        if not self.event.is_money:
            raise ValidationError('Можно выбирать только платные мероприятия')

    def __str__(self):
        """
        Строковое представление продажи.

        Возвращает строку с названием мероприятия и датой продажи.
        """
        return f'Продажа {self.event.name}, {self.date_sell}'


    class Meta:
        verbose_name = 'Продажа'
        verbose_name_plural = 'Продажи'


class BareSell(models.Model):
    """
    Модель для хранения информации об обычных продажах билетов.

    Атрибуты:
        sell (ForeignKey): Связь с продажей.
        money (PositiveIntegerField): Количество проданных билетов.
    """
    sell = models.ForeignKey(Sale, on_delete=models.CASCADE)
    money = models.PositiveIntegerField()

    def clean(self):
        """
        Валидация обычной продажи.

        Проверяет, что количество проданных билетов не превышает вместимость пространства.
        """
        if self.sell.event.spaces.volume < len(BareSell.objects.filter(sell__event__spaces=self.sell.event.spaces)):
            raise ValidationError('Слишком много билетов продано')

    class Meta:
        verbose_name = 'Обычная продажа'
        verbose_name_plural = 'Обычные продажи'


class Ticket(models.Model):
    """
    Модель для хранения информации о билетах.

    Атрибуты:
        location (ForeignKey): Связь с локацией.
        row (PositiveIntegerField): Номер ряда.
        column (PositiveIntegerField): Номер места.
        cost (PositiveIntegerField): Стоимость билета.
        sale (ForeignKey): Связь с продажей.
    """
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, verbose_name='Локация', blank=True)
    row = models.PositiveIntegerField('Номер ряда', blank=True, null=True)
    column = models.PositiveIntegerField('Номер места', blank=True, null=True)
    cost = models.PositiveIntegerField(verbose_name='Цена', null=True, blank=True)
    sale = models.ForeignKey(Sale, verbose_name='Продажа', on_delete=models.CASCADE)

    def clean(self):
        """
        Валидация билета.

        Проверяет доступность места в выбранной локации.
        """
        print(self.row)
        s = self.sale.ticketrow_set.all().get(location=self.location, row_number=self.row).available_numbers
        print(s, self.column, self.row, str(self.column) in s)
        if not str(self.column) in str(s).split():
            raise ValidationError('Место уже занято либо не существует')

    def __str__(self):
        """
        Строковое представление билета.

        Возвращает строку 'Билет'.
        """
        return 'Билет'
    
    class Meta:
        verbose_name = 'Билет'
        verbose_name_plural = 'Билеты'


class TicketAvailable(models.Model):
    """
    Модель для отображения доступности билетов.

    Атрибуты:
        column (PositiveIntegerField): Номер места.
        row (PositiveIntegerField): Номер ряда.
        location (ForeignKey): Связь с локацией.
        availability (BooleanField): Доступно ли место.
        sale (ForeignKey): Связь с продажей.
    """
    column = models.PositiveIntegerField('Номер места')
    row = models.PositiveIntegerField('Номер ряда')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name='Локация')
    availability = models.BooleanField(default=True, verbose_name='Доступно?')
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, verbose_name='Продажа')


    def __str__(self):
        """
        Строковое представление доступности билета.

        Возвращает строку 'Билет доступный'.
        """
        return 'Билет доступный'
    
    class Meta:
        verbose_name = 'Доступность билетов'
        verbose_name_plural = 'Доступности билетова'


class TicketRow(models.Model):
    """
    Модель для хранения информации о рядах билетов.

    Атрибуты:
        row_number (PositiveBigIntegerField): Номер ряда.
        available_numbers (CharField): Доступные номера мест.
        location (ForeignKey): Связь с локацией.
        sale (ForeignKey): Связь с продажей.
    """
    row_number = models.PositiveBigIntegerField('Номер ряда')
    available_numbers = models.CharField(max_length=500, verbose_name='Доступные места')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name='Локация')
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, verbose_name='Продажа')

    def __str__(self):
        """
        Строковое представление ряда билетов.

        Возвращает строку 'Ряды билетов'.
        """
        return 'Ряды билетов'


    class Meta:
        verbose_name = 'Ряд билетов'
        verbose_name_plural = 'Ряды билетов'


@receiver(post_save, sender=Sale)
def sale_ticket_availibily_creation(sender, instance, created, **kwargs):
    """
    Сигнал для создания доступных билетов при создании продажи.

    При создании новой продажи генерируются ряды билетов для каждой локации мероприятия.
    
    Args:
        sender: Отправитель сигнала.
        instance (Sale): Экземпляр продажи.
        created (bool): Флаг создания.
        **kwargs: Дополнительные аргументы.
    """
    if created:
        for location in instance.event.spaces.location_set.all():
            rows = location.row
            columns = location.amount
            for row in range(rows):
                TicketRow.objects.create(
                    row_number=row+1,
                    available_numbers=' '.join(map(str, range(1, columns+1))),
                    location=location,
                    sale=instance
                )
                # Для каждого ряда можно также создавать объекты TicketAvailable, если необходимо
                # for column in range(columns):
                #     TicketAvailable.objects.create(
                #         column=column+1,
                #         row=row+1,
                #         location=location,
                #         sale=instance,
                #         availability=True
                #     )


@receiver(post_save, sender=Ticket)
def create_ticket(sender, instance, created, *args, **kwargs):
    """
    Сигнал для обновления информации о билете после его создания.

    При создании билета автоматически устанавливается его стоимость и обновляется доступность места.
    
    Args:
        sender: Отправитель сигнала.
        instance (Ticket): Экземпляр билета.
        created (bool): Флаг создания.
        *args: Дополнительные аргументы.
        **kwargs: Дополнительные аргументы.
    """
    if created:
        location = instance.location
        cost = EventMoneyRelation.objects.filter(space=location).first().cost
        instance.cost = cost
        instance.save()
        rows_available = TicketRow.objects.get(row_number=instance.row, sale=instance.sale, location=instance.location)
        rows_available.available_numbers = ' '.join(
            filter(
                lambda x: x != str(instance.column),
                map(
                    str,
                    range(1, rows_available.location.amount+1)
                )
            )
        )
        rows_available.save()


@receiver(post_save, sender=Report)
def create_report(sender, instance, created, **kwargs):
    """
    Сигнал для создания строк отчета после его создания.

    При создании нового отчета собирается информация о продажах билетов за указанный период и создаются соответствующие строки отчета.
    
    Args:
        sender: Отправитель сигнала.
        instance (Report): Экземпляр отчета.
        created (bool): Флаг создания.
        **kwargs: Дополнительные аргументы.
    """
    if created:
        sales = Sale.objects.filter(
            date_sell__gte=instance.date_started,
            date_sell__lte=instance.date_end
        )
        report_dict = dict()
        for sale in sales:
            if sale.event.id not in report_dict.keys():
                report_dict.update({
                    sale.event.id: [0, 0, dict()]
                })
            tickets_all = report_dict[sale.event.id][0]
            tickets_sum = report_dict[sale.event.id][1]
            amounts = report_dict[sale.event.id][2]
            for ticket in sale.ticket_set.all():
                tickets_all += 1
                tickets_sum += ticket.cost
                if ticket.cost not in amounts.keys():
                    amounts.update({ticket.cost: 1})
                else:
                    amounts[ticket.cost] += 1
            report_dict[sale.event.id] = [
                tickets_all, 
                tickets_sum,
                amounts
            ]
        
        for i in report_dict.keys():
            rep_build = ''
            temp = report_dict[i][2]
            for value in temp.keys():
                rep_build += f'Цена:{value} - Количество проданных билетов: {temp[value]}\n'
            ReportRow.objects.create(
                event=Event.objects.get(id=i),
                amount=report_dict[i][0],
                cost=report_dict[i][1],
                description=rep_build,
                report=instance
            )