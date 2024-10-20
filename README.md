# Проект автоматизации культурного центра
## Описание проекта
Мы планируем разработать комплексную систему автоматизации для управления деятельностью культурного центра. Система будет охватывать три основных направления:
1. Развлекательная деятельность

2. Образовательная деятельность

3. Культурно-просветительская деятельность

Проект направлен на оптимизацию процессов управления пространствами, мероприятиями, студиями, экспонатами, а также на автоматизацию продажи билетов и формирования отчетности.
## Реализуемый функционал
### Управление пространствами и мероприятиями

- Создание, редактирование и удаление пространств с возможностью указания локаций

- Управление мероприятиями с привязкой к пространствам

- Установка цен на билеты для различных локаций мероприятий


### Образовательная деятельность

- Управление студиями и преподавателями

- Создание расписания работы студий

- Обработка заявок на посещение студий

### Культурно-просветительская деятельность

- Управление экспонатами и выставками

- Организация процесса проведения выставок, включая приказы и акты

### Продажа билетов и абонементов

- Система продажи билетов на мероприятия с учетом локаций

- Продажа абонементов на занятия в студиях

### Отчетность

- Формирование различных отчетов (о продажах, работе преподавателей, деятельности культурного центра)

### Импорт данных
- Возможность загрузки данных из Excel-файлов


## Архитектура

### Основные модели

1. `Prostranstvo` (Пространство)
   - Атрибуты:
     - name: CharField
     - volume: PositiveIntegerField
     - description: TextField
     - loc: BooleanField
   - Методы: clean(), upload_excel()

2. `Location` (Локация)
   - Атрибуты:
     - type: CharField (с выбором)
     - amount: PositiveIntegerField
     - row: PositiveIntegerField
     - space: ManyToManyField (к Prostranstvo)
   - Методы: suply()

3. `Event` (Мероприятие)
   - Атрибуты:
     - date: DateField
     - name: CharField
     - type: ForeignKey (к EventType)
     - time_started: TimeField
     - time_end: TimeField
     - users_amount: PositiveIntegerField
     - spaces: ForeignKey (к Prostranstvo)
     - is_money: BooleanField
     - description: TextField
   - Методы: clean()

4. `MoneyEvent` (Платное мероприятие)
   - Атрибуты:
     - event: ForeignKey (к Event)
   - Методы: clean()

5. `Studio` (Студия)
   - Атрибуты:
     - name: CharField
     - description: TextField
   - Методы: upload_excel()

6. `Teacher` (Преподаватель)
   - Атрибуты:
     - full_name: CharField
   - Методы: upload_excel()

7. `Exhibits` (Экспонат)
   - Атрибуты:
     - name: CharField
     - owner: ForeignKey (к ExhibitOwnerProxy)
   - Методы: upload_excel()

8. `Exhibition` (Выставка)
   - Атрибуты:
     - name: CharField
     - ex_type: CharField (с выбором)
     - description: TextField

9. `OrderToCreateExhibition` (Приказ о проведении выставки)
   - Атрибуты:
     - date_created: DateTimeField
     - exhibition: ForeignKey (к Exhibition)
     - date_start: DateTimeField
     - date_end: DateTimeField
     - place: ForeignKey (к Prostranstvo)

10. `Sale` (Продажа)
    - Атрибуты:
      - date_sell: DateTimeField
      - event: ForeignKey (к Event)

11. `Ticket` (Билет)
    - Атрибуты:
      - location: ForeignKey (к Location)
      - row: PositiveIntegerField
      - column: PositiveIntegerField
      - cost: PositiveIntegerField
      - sale: ForeignKey (к Sale)
    - Методы: clean()

12. `Report` (Отчет)
    - Атрибуты:
      - date_started: DateField
      - date_end: DateField

13. `EventType` (Тип мероприятия)
    - Атрибуты:
      - name: CharField

14. `Organization` (Организация)
    - Атрибуты:
      - name: CharField


### Вспомогательные классы и функции

1. `FileUpload` 
   - Для загрузки данных из Excel-файлов

2. Сигналы Django
   - Для автоматического создания связанных объектов и валидации данных

3. Прокси-модели
   - Для удобного управления объектами в админ-панели

4. Инлайн-классы для админки
   - Для отображения связанных объектов в админ-панели

### Дополнительные компоненты

1. Система аутентификации и авторизации
2. Механизм формирования и экспорта отчетов
4. Система валидации данных на уровне моделей и форм

Этот план-документация предоставляет общее представление о структуре и функциональности проекта. По мере разработки могут потребоваться дополнительные классы, методы и функции для реализации всего необходимого функционала.