from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from session1.models import Exhibits, ExhibitOwnerProxy, Organization, Exhibition, Prostranstvo
from django.core.exceptions import ValidationError
from typing import Any, Type


class ExhibitProxy(Exhibits):
    """
    Прокси-модель для Экспонатов.

    Используется для удобного управления экспонатами в админ-панели.
    """
    class Meta:
        proxy = True
        verbose_name = 'Экспонат'
        verbose_name_plural = 'Экспонаты'


class OrganizationProxy(Organization):
    """
    Прокси-модель для Организаций.

    Позволяет управлять организациями в админ-панели.
    """
    class Meta:
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'
    
    def __str__(self) -> str:
        """
        Строковое представление организации.

        Возвращает название организации.
        """
        return self.name


class ExhibitionProxy(Exhibition):
    """
    Прокси-модель для Выставок.

    Используется для управления выставками в админ-панели.
    """
    class Meta:
        verbose_name = 'Выставка'
        verbose_name_plural = 'Выставки'


class OrderToCreateExhibition(models.Model):
    """
    Модель для хранения информации о приказах на проведение выставок.

    Атрибуты:
        date_created (DateTimeField): Дата формирования приказа.
        exhibition (ForeignKey): Связь с моделью Exhibition.
        date_start (DateTimeField): Дата начала выставки.
        date_end (DateTimeField): Дата окончания выставки.
        place (ForeignKey): Связь с моделью Prostranstvo (пространство).
    """
    date_created = models.DateTimeField('Дата формирования приказа')
    exhibition = models.ForeignKey(Exhibition, verbose_name='Выставка', on_delete=models.CASCADE)
    date_start = models.DateTimeField('Дата начала выставки')
    date_end = models.DateTimeField('Дата окончания выставки')
    place = models.ForeignKey(Prostranstvo, verbose_name='Пространство', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Приказ о проведении выставки'
        verbose_name_plural = 'Приказы о проведении выставок'

    def __str__(self) -> str:
        """
        Строковое представление приказа.

        Возвращает строку с датой создания и названием выставки.
        """
        return f'Приказ о проведении ({self.date_created}, {self.exhibition})'


class OrderExhibitionFromAuthors(models.Model):
    """
    Модель для хранения приказов о получении экспонатов от сторонних авторов.

    Атрибуты:
        date_getting (DateTimeField): Дата получения экспонатов.
        creation_order (ForeignKey): Связь с моделью OrderToCreateExhibition.
    """
    date_getting = models.DateTimeField('Дата получения экспонатов')
    creation_order = models.ForeignKey(OrderToCreateExhibition, verbose_name='Приказ о проведении выставки', on_delete=models.CASCADE)

    def __str__(self) -> str:
        """
        Строковое представление приказа о получении экспонатов.

        Возвращает строку с информацией о связанном приказе на проведение выставки.
        """
        return f'Приказ о получении экспонатов: {self.creation_order}'

    def clean(self) -> None:
        """
        Валидация данных приказа.

        Проверяет, является ли тип выставки 'Внешняя'. Если нет, то генерирует ошибку.
        """
        if not self.creation_order.exhibition.ex_type == 'Внешняя':
            raise ValidationError('Вам не нужно заполнять этот приказ')
        
    class Meta:
        verbose_name = 'Приказ о поступлении экспонатов от сторонней стороны'
        verbose_name_plural = 'Приказы о поступлении экспонатов от сторонней стороны'


class OrderExhibitionToExhibit(models.Model):
    """
    Модель для хранения актов передачи экспонатов на выставку.

    Атрибуты:
        date_to_provide (DateTimeField): Дата передачи экспонатов.
        order_to_create_exhibit (ForeignKey): Связь с моделью OrderToCreateExhibition.
    """
    date_to_provide = models.DateTimeField('Дата передачи')
    order_to_create_exhibit = models.ForeignKey(OrderToCreateExhibition, verbose_name='Приказ о проведении выставки', on_delete=models.CASCADE)

    def __str__(self) -> str:
        """
        Строковое представление акта передачи экспонатов.

        Возвращает строку с информацией о связанном приказе на проведение выставки.
        """
        return f'Акт передачи экспонатов на выставку ({self.order_to_create_exhibit})'

    def clean(self) -> None:
        """
        Валидация данных акта передачи.

        Проверяет доступность экспонатов для бронирования и наличие актов поступления от сторонней организации при внешней выставке.
        """
        for exhibit in self.order_to_create_exhibit.exhibitauthormapping_set.all():
            fuck = len(ExhibitAuthorMapping.objects.filter(exhibit=exhibit.exhibit, order_to_get__isnull=False))
            fuck1 = len(ExhibitAuthorMapping.objects.filter(exhibit=exhibit.exhibit, order_to_return__isnull=False))
            if self.order_to_create_exhibit.exhibition.ex_type == 'Внешняя':
                if not fuck == fuck1 + 1:
                    raise ValidationError('Экспонат недоступен для бронирования')
            else:
                if not fuck == fuck1:
                    raise ValidationError('Экспонат недоступен для бронирования')
            if self.order_to_create_exhibit.exhibition.ex_type == 'Внешняя':
                if not len(self.order_to_create_exhibit.orderexhibitionfromauthors_set.all()):
                    raise ValidationError('Вы не заполнили поступление экспонатов от сторонней организации')

    class Meta:
        verbose_name = 'Акт передачи экспонатов на выставку'
        verbose_name_plural = 'Акты передачи экспонатов на выставку'


class OrderToReturn(models.Model):
    """
    Модель для хранения актов возврата экспонатов.

    Атрибуты:
        date_return (DateTimeField): Дата возврата экспонатов.
        order_to_create (ForeignKey): Связь с моделью OrderToCreateExhibition.
    """
    date_return = models.DateTimeField('Дата возврата экспонатов')
    order_to_create = models.ForeignKey(OrderToCreateExhibition, verbose_name='Приказ о проведении выставки', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Акт возврата экспонатов'
        verbose_name_plural = 'Акты возврата экспонатов'
    
    def clean(self) -> None:
        """
        Валидация данных акта возврата.

        Проверяет наличие акта приема передачи при внешней выставке.
        """
        if self.order_to_create.exhibition.ex_type == 'Внешняя':
                if not len(self.order_to_create.orderexhibitionfromauthors_set.all()):
                    raise ValidationError('Нет акта приема передачи')
    
    def __str__(self) -> str:
        """
        Строковое представление акта возврата экспонатов.

        Возвращает строку с информацией о связанном приказе на проведение выставки.
        """
        return f'Акт возврата экспонатов: {self.order_to_create}'


class ExhibitAuthorMapping(models.Model):
    """
    Модель для связывания экспонатов с их владельцами и приказами.

    Атрибуты:
        owner (CharField): Владелец экспоната.
        exhibit (ForeignKey): Связь с моделью Exhibits.
        order_to_create (ForeignKey): Связь с моделью OrderToCreateExhibition.
        order_to_get (ForeignKey): Связь с моделью OrderExhibitionFromAuthors.
        order_to_provide (ForeignKey): Связь с моделью OrderExhibitionToExhibit.
        order_to_return (ForeignKey): Связь с моделью OrderToReturn.
    """
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
def organization(sender: Type[OrganizationProxy], instance: OrganizationProxy, **kwargs: Any) -> None:
    """
    Сигнал для создания ExhibitOwnerProxy при сохранении OrganizationProxy.

    Args:
        sender (Type[OrganizationProxy]): Отправитель сигнала.
        instance (OrganizationProxy): Экземпляр организации.
        **kwargs (Any): Дополнительные аргументы.
    """
    ExhibitOwnerProxy.objects.create(org=instance)


@receiver(post_save, sender=ExhibitAuthorMapping)
def author_mapping(sender: Type[ExhibitAuthorMapping], instance: ExhibitAuthorMapping, created: bool, **kwargs: Any) -> None:
    """
    Сигнал для обновления владельца экспоната при создании ExhibitAuthorMapping.

    Args:
        sender (Type[ExhibitAuthorMapping]): Отправитель сигнала.
        instance (ExhibitAuthorMapping): Экземпляр ExhibitAuthorMapping.
        created (bool): Флаг создания.
        **kwargs (Any): Дополнительные аргументы.
    """
    if created:
        instance.owner = str(instance.exhibit.owner)
        instance.save()


@receiver(post_save, sender=OrderExhibitionToExhibit)
def get_exhibits(sender: Type[OrderExhibitionToExhibit], instance: OrderExhibitionToExhibit, created: bool, **kwargs: Any) -> None:
    """
    Сигнал для связывания экспонатов с актом передачи при создании OrderExhibitionToExhibit.

    Args:
        sender (Type[OrderExhibitionToExhibit]): Отправитель сигнала.
        instance (OrderExhibitionToExhibit): Экземпляр OrderExhibitionToExhibit.
        created (bool): Флаг создания.
        **kwargs (Any): Дополнительные аргументы.
    """
    if created:
        for exhibit in instance.order_to_create_exhibit.exhibitauthormapping_set.all():
            exhibit.order_to_provide = instance
            exhibit.save()


@receiver(post_save, sender=OrderExhibitionFromAuthors)
def get_exhibits_(sender: Type[OrderExhibitionFromAuthors], instance: OrderExhibitionFromAuthors, created: bool, **kwargs: Any) -> None:
    """
    Сигнал для связывания экспонатов с приказом о получении при создании OrderExhibitionFromAuthors.

    Args:
        sender (Type[OrderExhibitionFromAuthors]): Отправитель сигнала.
        instance (OrderExhibitionFromAuthors): Экземпляр OrderExhibitionFromAuthors.
        created (bool): Флаг создания.
        **kwargs (Any): Дополнительные аргументы.
    """
    if created:
        for exhibit in instance.creation_order.exhibitauthormapping_set.all():
            exhibit.order_to_get = instance
            exhibit.save()


@receiver(post_save, sender=OrderToReturn)
def get_exhibits_return(sender: Type[OrderToReturn], instance: OrderToReturn, created: bool, **kwargs: Any) -> None:
    """
    Сигнал для связывания экспонатов с актом возврата при создании OrderToReturn.

    Args:
        sender (Type[OrderToReturn]): Отправитель сигнала.
        instance (OrderToReturn): Экземпляр OrderToReturn.
        created (bool): Флаг создания.
        **kwargs (Any): Дополнительные аргументы.
    """
    if created:
        for exhibit in instance.order_to_create.exhibitauthormapping_set.all():
            exhibit.order_to_return = instance
            exhibit.save()


@receiver(post_save, sender=ExhibitAuthorMapping)
def check_exhibit_owner(sender: Type[ExhibitAuthorMapping], instance: ExhibitAuthorMapping, created: bool, **kwargs: Any) -> None:
    """
    Сигнал для проверки владельца экспоната после сохранения ExhibitAuthorMapping.

    Args:
        sender (Type[ExhibitAuthorMapping]): Отправитель сигнала.
        instance (ExhibitAuthorMapping): Экземпляр ExhibitAuthorMapping.
        created (bool): Флаг создания.
        **kwargs (Any): Дополнительные аргументы.
    """
    self = instance
    if self.order_to_create.exhibition.ex_type == 'Внешняя':
        if not self.exhibit.owner.org:
            raise ValidationError('Экспонаты должны принадлежать внешней организации')
    else:
        if self.exhibit.owner.org:
            raise ValidationError('Экспонаты должны принадлежать культурному центру либо студии')