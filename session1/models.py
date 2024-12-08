from django.db import models
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
import pandas
from django.core.exceptions import ValidationError
from typing import Any, Type


types = []


class Location(models.Model):
    """
    Модель для хранения информации о локациях в пространстве.

    Атрибуты:
        type (CharField): Тип локации (Партер, Амфитеатр, Балкон).
        amount (PositiveIntegerField): Количество мест в ряду.
        row (PositiveIntegerField): Количество рядов.
        space (ManyToManyField): Связь с моделью Prostranstvo.
    """
    type = models.CharField(choices=[('Партер', 'Партер'), ('Амфитеатр', 'Амфитеатр'), ('Балкон', 'Балкон')], verbose_name='Тип локации', max_length=100)
    amount = models.PositiveIntegerField('Мест в ряду', default=1)
    row = models.PositiveIntegerField('Рядов', default=1)
    space = models.ManyToManyField('Prostranstvo', verbose_name='Места')

    @property
    def suply(self) -> int:
        """
        Вычисляет общее количество мест в локации.

        Returns:
            int: Общее количество мест.
        """
        return self.row * self.amount

    def __str__(self) -> str:
        """
        Строковое представление локации.

        Возвращает строку с типом, количеством мест и привязанными пространствами.
        """
        return f'{self.type} ({self.row * self.amount} мест; {self.row} рядов, {self.amount} мест в ряде, пространства: {" ".join(map(lambda x: x.name, self.space.all()))})'


class EventType(models.Model):
    """
    Модель для хранения типов мероприятий.

    Атрибуты:
        name (CharField): Название типа мероприятия.
    """
    name = models.CharField('Название мероприятия', max_length=100)

    def __str__(self) -> str:
        """
        Строковое представление типа мероприятия.

        Возвращает название типа мероприятия.
        """
        return self.name


class Prostranstvo(models.Model):
    """
    Модель для хранения информации о пространствах.

    Атрибуты:
        name (CharField): Наименование пространства.
        volume (PositiveIntegerField): Вместимость пространства.
        description (TextField): Описание пространства.
        loc (BooleanField): Наличие локаций в пространстве.
    """
    name = models.CharField('Наименование', max_length=200)
    volume = models.PositiveIntegerField('Вместимость', default=1)
    description = models.TextField('Описание', default='')
    loc = models.BooleanField(default=False, verbose_name='Есть ли локации?')

    
    class Meta:
        verbose_name = 'Пространство'
        verbose_name_plural = 'Пространства'
    
    def clean(self, *args, **kwargs) -> None:
        """
        Валидация данных пространства.

        Проверяет согласованность наличия локаций и вместимости пространства.
        """
        if not self.loc:
            try:
                if len(self.location_set.all()):
                    raise ValidationError('Вы не можете установить локации потому что не нажали поле Есть ли локации')
            except:
                pass
        if self.loc and not len(self.location_set.all()):
            raise ValidationError('Вы не можете сохранить объект, выберите хотябы одну локацию')
        locs = 0
        try:
            for i in self.location_set.all():
                locs += i.suply
            if locs > self.volume:
                raise ValidationError(f'Вы не можете добавить локаций так как вместимость пространства: {self.volume}, а суммарная вместимость всех локаций: {locs}')
        except: pass    
        super(Prostranstvo, self).save(*args, **kwargs)
    
    def __str__(self) -> str:
        """
        Строковое представление пространства.

        Возвращает наименование пространства.
        """
        return self.name
    
    @staticmethod
    def upload_excel(value: list) -> None:
        """
        Статический метод для загрузки данных из Excel.

        Args:
            value (list): Список значений для создания или получения пространства.
        """
        try:
            Prostranstvo.objects.get(name=value[0], volume=value[1], description=value[2])
        except Prostranstvo.DoesNotExist:
            Prostranstvo.objects.create(name=value[0], volume=value[1], description=value[2])


class Event(models.Model):
    """
    Модель для хранения информации о мероприятиях.

    Атрибуты:
        date (DateField): Дата проведения мероприятия.
        name (CharField): Название мероприятия.
        type (ForeignKey): Связь с моделью EventType.
        time_started (TimeField): Время начала мероприятия.
        time_end (TimeField): Время окончания мероприятия.
        users_amount (PositiveIntegerField): Количество посетителей.
        spaces (ForeignKey): Связь с моделью Prostranstvo.
        is_money (BooleanField): Является ли мероприятие платным.
        description (TextField): Описание мероприятия.
    """
    date = models.DateField('Дата проведения')
    name = models.CharField('Название', max_length=200)
    type = models.ForeignKey(EventType, verbose_name='Тип мероприятия', on_delete=models.CASCADE)
    time_started = models.TimeField('Время начала')
    time_end = models.TimeField('Время окончания')
    users_amount = models.PositiveIntegerField('Количество поситителей')
    spaces = models.ForeignKey(Prostranstvo, verbose_name='Пространство', on_delete=models.CASCADE, null=True)
    is_money = models.BooleanField('Платно?', default=False)
    description = models.TextField(default='', verbose_name='Описание')

    def clean(self) -> None:
        """
        Валидация данных мероприятия.

        Проверяет вместимость пространства и корректность времени проведения.
        """
        if self.spaces.volume < self.users_amount:
            raise ValidationError('В этом пространстве не хватает мест, выберите другое')
        if self.time_started > self.time_end:
            raise ValidationError('Время начало позже времени конца')

    def __str__(self) -> str:
        """
        Строковое представление мероприятия.

        Возвращает название мероприятия с указанием его типа и пространства.
        """
        m = 'Бесплатное'
        if self.is_money:
            m = 'Платное'
        return self.name + f'({m}, Пространство: {self.spaces.name})'


class MoneyEvent(models.Model):
    """
    Модель для хранения информации о платных мероприятиях.

    Атрибуты:
        event (ForeignKey): Связь с моделью Event.
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name='Мероприятие')

    def __str__(self) -> str:
        """
        Строковое представление платного мероприятия.

        Возвращает строку с информацией о мероприятии.
        """
        return f'Установка цен на {str(self.event)}'
    
    def clean(self) -> None:
        """
        Валидация данных платного мероприятия.

        Проверяет, что мероприятие является платным и выбирает корректные локации.
        """
        if not self.event.is_money:
            raise ValidationError('Выберите платное событие')
        space = self.event.spaces
        allowed_locs = Location.objects.filter(space=space)
        try:
            our_locs = self.eventmoneyrelation_set.all()
            for rel in our_locs:
                if not rel.space in allowed_locs:
                    raise ValidationError('Можно выбрать лишь те локации, которые относятся к пространству проведения мероприятия')
            print(our_locs, allowed_locs)
        except Exception as e:
            print(e)
            if isinstance(e, ValidationError):
                raise e
            else:
                raise ValidationError('Выберите локации')


class EventMoneyRelation(models.Model):
    """
    Модель для связи мероприятий с локациями и их стоимостью.

    Атрибуты:
        space (ForeignKey): Связь с моделью Location.
        cost (PositiveIntegerField): Стоимость за место.
        money_event (ForeignKey): Связь с моделью MoneyEvent.
    """
    space = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name='Пространство')
    cost = models.PositiveIntegerField('Цена за место')
    money_event = models.ForeignKey(MoneyEvent, on_delete=models.CASCADE)

    def __str__(self) -> str:
        """
        Строковое представление связи мероприятия с локацией.

        Возвращает строку с информацией о локации и цене.
        """
        return f'Пространство: {self.space}, Цена: {self.cost}'
    
    def clean(self) -> None:
        """
        Валидация данных связи мероприятия с локацией.
        """
        pass


class Studio(models.Model):
    """
    Модель для хранения информации о студиях.

    Атрибуты:
        name (CharField): Наименование студии.
        description (TextField): Описание студии.
    """
    name = models.CharField('Наименование', max_length=200, unique=True)
    description = models.TextField('Описание', default='')

    class Meta:
        verbose_name = 'Студия'
        verbose_name_plural = 'Студии'
    
    @staticmethod
    def upload_excel(value: list) -> None:
        """
        Статический метод для загрузки данных студии из Excel.

        Args:
            value (list): Список значений для создания или получения студии.
        """
        try:
            Studio.objects.get(name=value[0], description=value[1])
        except Studio.DoesNotExist:
            Studio.objects.create(name=value[0], description=value[1])
    
    def __str__(self) -> str:
        """
        Строковое представление студии.

        Возвращает наименование студии.
        """
        return self.name


class ProstrSutdioMapping(models.Model):
    """
    Модель для связи студий с пространствами.

    Атрибуты:
        studio (ForeignKey): Связь с моделью Studio.
        prostr (ForeignKey): Связь с моделью Prostranstvo.
    """
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE, null=True)
    prostr = models.ForeignKey(Prostranstvo, on_delete=models.CASCADE, null=True)

    def __str__(self) -> str:
        """
        Строковое представление связи студии с пространством.

        Возвращает наименование студии или пространства.
        """
        if self.studio:
            return str(self.studio)
        if self.prostr:
            return str(self.prostr)


class Teacher(models.Model):
    """
    Модель для хранения информации о преподавателях.

    Атрибуты:
        full_name (CharField): Полное имя преподавателя.
    """
    full_name = models.CharField('ФИО', max_length=300, unique=True)

    def __str__(self) -> str:
        """
        Строковое представление преподавателя.

        Возвращает полное имя преподавателя.
        """
        return self.full_name
    
    @staticmethod
    def upload_excel(value: list) -> None:
        """
        Статический метод для загрузки данных преподавателя из Excel.

        Args:
            value (list): Список значений для создания или получения преподавателя.
        """
        try:
            Teacher.objects.get(full_name=value[0])
        except Teacher.DoesNotExist:
            Teacher.objects.create(full_name=value[0])


class Exhibition(models.Model):
    """
    Модель для хранения информации о выставках.

    Атрибуты:
        name (CharField): Название выставки.
        ex_type (CharField): Тип выставки (Внутренняя, Внешняя).
        description (TextField): Описание выставки.
    """
    name = models.CharField('Название', max_length=100)
    ex_type = models.CharField(
        choices=[('Внутренняя', 'Внутрення'), ('Внешняя', 'Внешняя')], verbose_name='Тип выставки', max_length=200)
    description = models.TextField('Описание')

    def __str__(self) -> str:
        """
        Строковое представление выставки.

        Возвращает название выставки.
        """
        return f'{self.name}'


class Organization(models.Model):
    """
    Модель для хранения информации об организациях.

    Атрибуты:
        name (CharField): Наименование организации.
    """
    name = models.CharField('Наименование организации', max_length=100)

    class Meta:
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'
    
    def __str__(self) -> str:
        """
        Строковое представление организации.

        Возвращает наименование организации.
        """
        return self.name


class ExhibitOwnerProxy(models.Model):
    """
    Модель-прокси для владельцев экспонатов (организации или студии).

    Атрибуты:
        org (ForeignKey): Связь с моделью Organization.
        studio (ForeignKey): Связь с моделью Studio.
    """
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True)
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE, null=True)

    def __str__(self) -> str:
        """
        Строковое представление владельца экспоната.

        Возвращает наименование организации или студии.
        """
        if self.org:
            return str(self.org)
        else:
            return str(self.studio)
    
    class Meta:
        verbose_name = 'Студия или Организация'
        verbose_name_plural = 'Студии или организации'


class Exhibits(models.Model):
    """
    Модель для хранения информации об экспонатах.

    Атрибуты:
        name (CharField): Наименование экспоната.
        owner (ForeignKey): Связь с моделью ExhibitOwnerProxy.
    """
    name = models.CharField('Наименование', max_length=200)
    owner = models.ForeignKey(ExhibitOwnerProxy, verbose_name='Владелец', on_delete=models.CASCADE)

    @staticmethod
    def upload_excel(value: list) -> None:
        """
        Статический метод для загрузки данных экспоната из Excel.

        Args:
            value (list): Список значений для создания или получения экспоната.
        """
        own, _ = Studio.objects.get_or_create(name=value[1])
        try:
            Exhibits.objects.get(name=value[0], owner=own)
        except Exhibits.DoesNotExist:
            Exhibits.objects.create(name=value[0], owner=own)
    
    def __str__(self) -> str:
        """
        Строковое представление экспоната.

        Возвращает наименование экспоната.
        """
        return self.name


class FileUpload(models.Model):
    """
    Модель для хранения загруженных файлов.

    Атрибуты:
        type (CharField): Тип файла (Пространство, Экспонат, Студия, Преподаватель).
        file (FileField): Сам файл.
    """
    type = models.CharField(
        choices=[('Пространство', 'Пространство'), ('Экспонат', 'Экспонат'), ('Студия', 'Студия'), ('Преподаватель', 'Преподаватель')],
        max_length=200, verbose_name='Тип файла')
    file = models.FileField('Файл')

    def __str__(self) -> str:
        """
        Строковое представление загрузки файла.

        Возвращает строку с информацией о типе файла.
        """
        return f'Загрузка файлов ({self.type})'

    class Meta:
        verbose_name = 'Загрузка файлов'
        verbose_name_plural = 'Загрузки файлов'


type_mappings = {
    'Пространство': Prostranstvo,
    'Экспонат': Exhibits,
    'Студия': Studio,
    'Преподаватель': Teacher
}


@receiver(post_save, sender=FileUpload)
def upload_file(sender: Type[FileUpload], instance: FileUpload, created: bool, **kwargs: Any) -> None:
    """
    Сигнал для обработки загруженных файлов после их сохранения.

    Читает данные из Excel и загружает их в соответствующие модели.

    Args:
        sender (Type[FileUpload]): Отправитель сигнала.
        instance (FileUpload): Экземпляр FileUpload.
        created (bool): Флаг создания.
        **kwargs (Any): Дополнительные аргументы.
    """
    df = pandas.read_excel(instance.file.path)
    if not created:
        return
    for val in df.values.tolist():
        type_mappings[instance.type].upload_excel(val)


@receiver(post_save, sender=Organization)
def organization(sender: Type[Organization], instance: Organization, *args: Any, **kwargs: Any) -> None:
    """
    Сигнал для создания ExhibitOwnerProxy при сохранении Organization.

    Args:
        sender (Type[Organization]): Отправитель сигнала.
        instance (Organization): Экземпляр организации.
        *args (Any): Дополнительные аргументы.
        **kwargs (Any): Дополнительные аргументы.
    """
    ExhibitOwnerProxy.objects.create(org=instance)


@receiver(post_save, sender=Studio)
def studio(sender: Type[Studio], instance: Studio, *args: Any, **kwargs: Any) -> None:
    """
    Сигнал для создания ExhibitOwnerProxy при сохранении Studio.

    Args:
        sender (Type[Studio]): Отправитель сигнала.
        instance (Studio): Экземпляр студии.
        *args (Any): Дополнительные аргументы.
        **kwargs (Any): Дополнительные аргументы.
    """
    ExhibitOwnerProxy.objects.create(studio=instance)


@receiver(post_save, sender=EventMoneyRelation)
def money_event_validation(sender: Type[EventMoneyRelation], instance: EventMoneyRelation, *args: Any, **kwargs: Any) -> None:
    """
    Сигнал для валидации связи мероприятия с локацией после сохранения EventMoneyRelation.

    Args:
        sender (Type[EventMoneyRelation]): Отправитель сигнала.
        instance (EventMoneyRelation): Экземпляр EventMoneyRelation.
        *args (Any): Дополнительные аргументы.
        **kwargs (Any): Дополнительные аргументы.
    """
    self = instance.money_event
    if not self.event.is_money:
        raise ValidationError('Выберите платное событие')
    space = self.event.spaces
    f = False
    allowed_locs = Location.objects.filter(space=space)
    try:
        our_locs = self.eventmoneyrelation_set.all()
        for rel in our_locs:
            if not rel.space in allowed_locs:
                raise ValidationError('Можно выбрать лишь те локации, которые относятся к пространству проведения мероприятия')
        print(our_locs, allowed_locs)
    except Exception as e:
        print(e)
        if isinstance(e, ValidationError):
            raise e
        else:
            raise ValidationError('Выберите локации')
