from django.db import models
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
import pandas
from django.core.exceptions import ValidationError


types = []


class Location(models.Model):
    type = models.CharField(choices=[('Партер', 'Партер'), ('Амфитеатр', 'Амфитеатр'), ('Балкон', 'Балкон')], verbose_name='Тип локации', max_length=100)
    amount = models.PositiveIntegerField('Мест в ряду', default=1)
    row = models.PositiveIntegerField('Рядов', default=1)
    space = models.ManyToManyField('Prostranstvo', verbose_name='Места')

    @property
    def suply(self):
        return self.row * self.amount

    def __str__(self):
        return f'{self.type} ({self.row * self.amount} мест; {self.row} рядов, {self.amount} мест в ряде, пространства: {" ".join(map(lambda x: x.name, self.space.all()))})'



class EventType(models.Model):
    name = models.CharField('Название мероприятия', max_length=100)

    def __str__(self): return self.name


class Prostranstvo(models.Model):
    name = models.CharField('Наименование', max_length=200)
    volume = models.PositiveIntegerField('Вместимость', default=1)
    description = models.TextField('Описание', default='')
    loc = models.BooleanField(default=False, verbose_name='Есть ли локации?')

    
    class Meta:
        verbose_name = 'Пространство'
        verbose_name_plural = 'Пространства'
    
    def clean(self, *args, **kwargs):
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
    
    def __str__(self):
        return self.name
    
    @staticmethod
    def upload_excel(value):
        try:
            Prostranstvo.objects.get(name=value[0], volume=value[1], description=value[2])
        except:
            Prostranstvo.objects.create(name=value[0], volume=value[1], description=value[2])


class Event(models.Model):
    date = models.DateField('Дата проведения')
    name = models.CharField('Название', max_length=200)
    type = models.ForeignKey(EventType, verbose_name='Тип мероприятия', on_delete=models.CASCADE)
    time_started = models.TimeField('Время начала')
    time_end = models.TimeField('Время окончания')
    users_amount = models.PositiveIntegerField('Количество поситителей')
    spaces = models.ForeignKey(Prostranstvo, verbose_name='Пространство', on_delete=models.CASCADE, null=True)
    is_money = models.BooleanField('Платно?', default=False)
    description = models.TextField(default='', verbose_name='Описание')

    def clean(self):
        if self.spaces.volume < self.users_amount:
            raise ValidationError('В этом пространстве не хватает мест, выберите другое')
        if self.time_started > self.time_end:
            raise ValidationError('Время начало позже времени конца')



    def __str__(self):
        m = 'Бесплатное'
        if self.is_money:
            m = 'Платное'
        return self.name + f'({m}, Пространство: {self.spaces.name})'


class MoneyEvent(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name='Мероприятие')

    def __str__(self):
        return f'Установка цен на {str(self.event)}'
    
    def clean(self):
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
            # if not len(our_locs) == len(allowed_locs):
            #     raise ValidationError('Выбраны не все локации которые привязаны к этому пространству')
        except Exception as e:
            print(e)
            if isinstance(e, ValidationError):
                raise e
            else:
                raise ValidationError('Выберите локации')
        


class EventMoneyRelation(models.Model):
    space = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name='Пространство')
    cost = models.PositiveIntegerField('Цена за место')
    money_event = models.ForeignKey(MoneyEvent, on_delete=models.CASCADE)

    def __str__(self):
        return f'Пространство: {self.space}, Цена: {self.cost}'
    
    def clean(self):
        pass


class Studio(models.Model):
    name = models.CharField('Наименование', max_length=200, unique=True)
    description = models.TextField('Описание', default='')

    class Meta:
        verbose_name = 'Студия'
        verbose_name_plural = 'Студии'
    
    @staticmethod
    def upload_excel(value):
        try:
            Studio.objects.get(name=value[0], description=value[1])
        except:
            Studio.objects.create(name=value[0], description=value[1])
    
    def __str__(self):
        return self.name


class ProstrSutdioMapping(models.Model):
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE, null=True)
    prostr = models.ForeignKey(Prostranstvo, on_delete=models.CASCADE, null=True)

    def __str__(self):
        if self.studio:
            return str(self.studio)
        if self.prostr:
            return str(self.prostr)


class Teacher(models.Model):
    full_name = models.CharField('ФИО', max_length=300, unique=True)

    def __str__(self):
        return self.full_name
    
    @staticmethod
    def upload_excel(value):
        try:
            Teacher.objects.get(full_name=value[0])
        except:
            Teacher.objects.create(full_name=value[0])


class Exhibition(models.Model):
    name = models.CharField('Название', max_length=100)
    ex_type = models.CharField(
        choices=[('Внутренняя', 'Внутрення'), ('Внешняя', 'Внешняя')], verbose_name='Тип выставки', max_length=200)
    description = models.TextField('Описание')

    def __str__(self):
        return f'{self.name}'


class Organization(models.Model):
    name = models.CharField('Наименование организации', max_length=100)

    class Meta:
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'
    
    def __str__(self):
        return self.name


class ExhibitOwnerProxy(models.Model):
    org = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True)
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE, null=True)

    def __str__(self):
        if self.org:
            return str(self.org)
        else:
            return str(self.studio)
    
    class Meta:
        verbose_name = 'Студия или Организация'
        verbose_name_plural = 'Студии или организации'


class Exhibits(models.Model):
    name = models.CharField('Наименование', max_length=200)
    owner = models.ForeignKey(ExhibitOwnerProxy, verbose_name='Владелец', on_delete=models.CASCADE)

    @staticmethod
    def upload_excel(value):
        own, _ = Studio.objects.get_or_create(name=value[1])
        try:
            Exhibits.objects.get(name=value[0], owner=own)
        except Exhibits.DoesNotExist:
            Exhibits.objects.create(name=value[0], owner=own)
    
    def __str__(self):
        return self.name


class FileUpload(models.Model):
    type = models.CharField(
        choices=[('Пространство', 'Пространство'), ('Экспонат', 'Экспонат'), ('Студия', 'Студия'), ('Преподаватель', 'Преподаватель')],
        max_length=200, verbose_name='Тип файла')
    file = models.FileField('Файл')

    def __str__(self):
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
def upload_file(sender, instance, created, **kwargs):
    df = pandas.read_excel(instance.file.path)
    if not created: return
    for val in df.values.tolist():
        type_mappings[instance.type].upload_excel(val)


@receiver(post_save, sender=Organization)
def organization(sender, instance, *args, **kwargs):
    ExhibitOwnerProxy.objects.create(org=instance)


@receiver(post_save, sender=Studio)
def studio(sender, instance, *args, **kwargs):
    ExhibitOwnerProxy.objects.create(studio=instance)


@receiver(post_save, sender=EventMoneyRelation)
def money_event_validation(sender, instance, *args, **kwargs):
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
        # if not len(our_locs) == len(allowed_locs):
        #     raise ValidationError('Выбраны не все локации которые привязаны к этому пространству')
    except Exception as e:
        print(e)
        if isinstance(e, ValidationError):
            raise e
        else:
            raise ValidationError('Выберите локации')