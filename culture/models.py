from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from session1.models import Exhibits, ExhibitOwnerProxy, Organization, Exhibition, Prostranstvo
from django.core.exceptions import ValidationError
from django.db.models.signals import ModelSignal
from typing import Any


class ExhibitProxy(Exhibits):
    class Meta:
        proxy = True
        verbose_name = 'Экспонат'
        verbose_name_plural = 'Экспонаты'


class OrganizationProxy(Organization):
    class Meta:
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'
    
    def __str__(self) -> str:
        return self.name


class ExhibitionProxy(Exhibition):
    class Meta:
        verbose_name = 'Выставка'
        verbose_name_plural = 'Выставки'


class OrderToCreateExhibition(models.Model):
    date_created = models.DateTimeField('Дата формирования приказа')
    exhibition = models.ForeignKey(Exhibition, verbose_name='Выставка', on_delete=models.CASCADE)
    date_start = models.DateTimeField('Дата начала выставки')
    date_end = models.DateTimeField('Дата окончания выставки')
    place = models.ForeignKey(Prostranstvo, verbose_name='Пространство', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Приказ о проведении выставки'
        verbose_name_plural = 'Приказы о проведении выставок'


    def __str__(self) -> str:
        return f'Приказ о проведении ({self.date_created}, {self.exhibition})'


class OrderExhibitionFromAuthors(models.Model):
    date_getting = models.DateTimeField('Дата получения экспонатов')
    creation_order = models.ForeignKey(OrderToCreateExhibition, verbose_name='Приказ о проведении выставки', on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'Приказ о получении экспонатов: {self.creation_order}'

    def clean(self) -> None:
        if not self.creation_order.exhibition.ex_type == 'Внешняя':
            raise ValidationError('Вам не нужно заполнять этот приказ')
        

    class Meta:
        verbose_name = 'Приказ о поступлении экспонатов от сторонней стороны'
        verbose_name_plural = 'Приказы о поступлении экспонатов от сторонней стороны'


class OrderExhibitionToExhibit(models.Model):
    date_to_provide = models.DateTimeField('Дата передачи')
    order_to_create_exhibit = models.ForeignKey(OrderToCreateExhibition, verbose_name='Приказ о проведении выставки', on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'Акт передачи экспонатов на выставку ({self.order_to_create_exhibit})'

    def clean(self) -> None:
        for exhibit in self.order_to_create_exhibit.exhibitauthormapping_set.all():
            fuck = len(ExhibitAuthorMapping.objects.filter(exhibit=exhibit.exhibit, order_to_get__isnull=False))
            fuck1 = len(ExhibitAuthorMapping.objects.filter(exhibit=exhibit.exhibit, order_to_return__isnull=False))
            if self.order_to_create_exhibit.exhibition.ex_type == 'Внешняя':
                if not fuck  == fuck1 + 1:
                    raise ValidationError('Экспонат недоступен для бронирования')
            else:
                if not fuck == fuck1:
                    raise ValidationError('Экспонат недоступен для бронирования')
            if self.order_to_create_exhibit.exhibition.ex_type == 'Внешняя':
                if not len(self.order_to_create_exhibit.orderexhibitionfromauthors_set.all()):
                    raise ValidationError('Вы не заполнили поступление экспонатов от сторонней организации')


    class Meta:
        verbose_name = 'Акт передачи экспонатов на выставку'
        verbose_name_plural = 'Акты передачи ��кспонатов на выставку'


class OrderToReturn(models.Model):
    date_return = models.DateTimeField('Дата возврата экспонатов')
    order_to_create = models.ForeignKey(OrderToCreateExhibition, verbose_name='Приказ о проведении выставки', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Акт возврата экспонатов'
        verbose_name_plural = 'Акты возврата экспонатов'
    
    def clean(self) -> None:
        if self.order_to_create.exhibition.ex_type == 'Внешняя':
                if not len(self.order_to_create.orderexhibitionfromauthors_set.all()):
                    raise ValidationError('Нет акта приема передачи')
    
    def __str__(self) -> str:
        return f'Акт возврата экспонатов: {self.order_to_create}'


class ExhibitAuthorMapping(models.Model):
    owner = models.CharField('Владелец', max_length=300)
    exhibit = models.ForeignKey(Exhibits, verbose_name='Экспонат', on_delete=models.CASCADE)
    order_to_create = models.ForeignKey(OrderToCreateExhibition, verbose_name='Приказ о проведении выставки', on_delete=models.CASCADE)
    order_to_get = models.ForeignKey(OrderExhibitionFromAuthors, verbose_name='Приказ о получении', null=True, on_delete=models.CASCADE)
    order_to_provide = models.ForeignKey(OrderExhibitionToExhibit, verbose_name='Акт передачи экспонатов на выставку', null=True, on_delete=models.CASCADE)
    order_to_return = models.ForeignKey(OrderToReturn, verbose_name='Акт возврата экспоната', null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Маршрут'
        verbose_name_plural = 'Маршруты'
    


@receiver(post_save, sender=OrganizationProxy)
def organization(sender: type, instance: OrganizationProxy, **kwargs: Any) -> None:
    ExhibitOwnerProxy.objects.create(org=instance)


@receiver(post_save, sender=ExhibitAuthorMapping)
def author_mapping(sender: type, instance: ExhibitAuthorMapping, created: bool, **kwargs: Any) -> None:
    if created:
        instance.owner = str(instance.exhibit.owner)
        instance.save()


@receiver(post_save, sender=OrderExhibitionToExhibit)
def get_exhibits(sender: type, instance: OrderExhibitionToExhibit, created: bool, **kwargs: Any) -> None:
    if created:
        for exhibit in instance.order_to_create_exhibit.exhibitauthormapping_set.all():
            exhibit.order_to_provide = instance
            exhibit.save()


@receiver(post_save, sender=OrderExhibitionFromAuthors)
def get_exhibits_(sender: type, instance: OrderExhibitionFromAuthors, created: bool, **kwargs: Any) -> None:
    if created:
        for exhibit in instance.creation_order.exhibitauthormapping_set.all():
            exhibit.order_to_get = instance
            exhibit.save()


@receiver(post_save, sender=OrderToReturn)
def get_exhibits_return(sender: type, instance: OrderToReturn, created: bool, **kwargs: Any) -> None:
    if created:
        for exhibit in instance.order_to_create.exhibitauthormapping_set.all():
            exhibit.order_to_return = instance
            exhibit.save()


@receiver(post_save, sender=ExhibitAuthorMapping)
def check_exhibit_owner(sender: type, instance: ExhibitAuthorMapping, created: bool, **kwargs: Any) -> None:
    self = instance
    if self.order_to_create.exhibition.ex_type == 'Внешняя':
        if not self.exhibit.owner.org:
            raise ValidationError('Экспонаты должны принадлежать внешней организации')
    else:
        if self.exhibit.owner.org:
            raise ValidationError('Экспонаты должны принадлежать культурному центру либо студии')