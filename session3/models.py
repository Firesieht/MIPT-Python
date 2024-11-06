from django.db import models
from session1.models import Event, Location, EventMoneyRelation
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError



class Report(models.Model):
    date_started = models.DateField('Дата начала')
    date_end = models.DateField('Дата конца')

    def clean(self):
        if self.date_end < self.date_started:
            raise ValidationError('Дата конца не может быть раньше даты начала')

    def __str__(self):
        return f'Отчет ({self.date_started} - {self.date_end})'
    

    class Meta:
        verbose_name = 'Отчет'
        verbose_name_plural = 'Отчеты'


class ReportRow(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name='Мероприятие')
    amount = models.PositiveIntegerField('Количество проданных билетов')
    cost = models.PositiveIntegerField('Их стоимость')
    report = models.ForeignKey(Report, on_delete=models.CASCADE, verbose_name='Отчет')
    description = models.CharField(max_length=300, verbose_name='Описание', null=True)

    def __str__(self):
        return ''
    
    class Meta:
        verbose_name = 'Объект отчета'
        verbose_name_plural = 'Объекты отчета'


class Sale(models.Model):
    date_sell = models.DateTimeField('Дата продажи', auto_now_add=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name='Мероприятие')

    def clean(self):
        if not self.event.is_money:
            raise ValidationError('Можно выбирать только платные мероприятия')

    def __str__(self):
        return f'Продажа {self.event.name}, {self.date_sell}'


    class Meta:
        verbose_name = 'Продажа'
        verbose_name_plural = 'Продажи'


class BareSell(models.Model):
    sell = models.ForeignKey(Sale, on_delete=models.CASCADE)
    money = models.PositiveIntegerField()


    def clean(self):
        if self.sell.event.spaces.volume < len(BareSell.objects.filter(sell__event__spaces=self.sell.event.spaces)):
            raise ValidationError('Слишком много билетов продано')

    class Meta:
        verbose_name = 'Обычная продажа'
        verbose_name_plural = 'Обычные продажи'


class Ticket(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, verbose_name='Локация', blank=True)
    row = models.PositiveIntegerField('Номер ряда', blank=True, null=True)
    column = models.PositiveIntegerField('Номер места', blank=True, null=True)
    cost = models.PositiveIntegerField(verbose_name='Цена', null=True, blank=True)
    sale = models.ForeignKey(Sale, verbose_name='Продажа', on_delete=models.CASCADE)

    def clean(self):
        print(self.row)
        s = self.sale.ticketrow_set.all().get(location=self.location, row_number=self.row).available_numbers
        print(s, self.column, self.row, str(self.column) in s)
        if not str(self.column) in str(s).split():
            raise ValidationError('Место уже занято либо не существует')

    def __str__(self):
        return 'Билет'
    
    class Meta:
        verbose_name = 'Билет'
        verbose_name_plural = 'Билеты'


class TicketAvailable(models.Model):
    column = models.PositiveIntegerField('Номер места')
    row = models.PositiveIntegerField('Номер ряда')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name='Локация')
    availability = models.BooleanField(default=True, verbose_name='Доступно?')
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, verbose_name='Продажа')


    def __str__(self):
        return 'Билет доступный'
    
    class Meta:
        verbose_name = 'Доступность билетов'
        verbose_name_plural = 'Доступности билетова'

class TicketRow(models.Model):
    row_number = models.PositiveBigIntegerField('Номер ряда')
    available_numbers = models.CharField(max_length=500, verbose_name='Доступные места')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name='Локация')
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, verbose_name='Продажа')

    def __str__(self):
        return 'Ряды билетов'


    class Meta:
        verbose_name = 'Ряд билетов'
        verbose_name_plural = 'Ряды билетов'


@receiver(post_save, sender=Sale)
def sale_ticket_availibily_creation(sender, instance, created, **kwargs):
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
def create_report(sender, instance, created, *args, **kwargs):
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