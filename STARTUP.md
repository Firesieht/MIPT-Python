# Инструкция по запуску Django проекта

Данная инструкция поможет вам настроить и запустить проект автоматизации культурного центра на вашем локальном компьютере.

## Требования

- **Python**: версии 3.8 и выше
- **pip**: пакетный менеджер для Python
- **virtualenv**: для создания виртуального окружения
- **PostgreSQL**: (опционально) в случае использования PostgreSQL вместо SQLite

## Шаги по запуску проекта

# Инструкция по запуску Django проекта

Данная инструкция поможет вам настроить и запустить проект автоматизации культурного центра на вашем локальном компьютере.

## Требования

- **Python**: версии 3.8 и выше
- **pip**: пакетный менеджер для Python
- **virtualenv**: для создания виртуального окружения
- **PostgreSQL**: (опционально) в случае использования PostgreSQL вместо SQLite

## Шаги по запуску проекта

### 1. Клонирование репозитория

Сначала необходимо клонировать репозиторий проекта на ваш локальный компьютер.


bash
git clone https://github.com/your-username/your-repo.git
```


### 2. Создание виртуального окружения

Создайте и активируйте виртуальное окружение для изоляции зависимостей проекта.

```bash
python3 -m venv venv
source venv/bin/activate # Для Windows: venv\Scripts\activate
```


### 3. Установка зависимостей

Установите все необходимые зависимости из файла `requirements.txt`.

```bash
pip install --upgrade pip
pip install -r requirements.txt
```


### 4. Настройка базы данных

В проекте предусмотрена поддержка SQLite и PostgreSQL. По умолчанию используется SQLite. Если вы хотите использовать PostgreSQL, выполните следующие шаги:

1. Установите PostgreSQL на ваш компьютер.
2. Создайте базу данных и пользователя.
3. Откройте файл настроек Django `project/settings.py` и измените параметры базы данных:

    ```python
    # project/settings.py

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'имя_базы_данных',
            'USER': 'ваш_пользователь',
            'PASSWORD': 'ваш_пароль',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }
    ```

### 5. Применение миграций

Создайте необходимые таблицы в базе данных, применив миграции.

```bash
python manage.py migrate
```


### 4. Настройка базы данных

В проекте предусмотрена поддержка SQLite и PostgreSQL. По умолчанию используется SQLite. Если вы хотите использовать PostgreSQL, выполните следующие шаги:

1. Установите PostgreSQL на ваш компьютер.
2. Создайте базу данных и пользователя.
3. Откройте файл настроек Django `project/settings.py` и измените параметры базы данных:

    ```python
    # project/settings.py

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'имя_базы_данных',
            'USER': 'ваш_пользователь',
            'PASSWORD': 'ваш_пароль',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }
    ```

### 5. Применение миграций

Создайте необходимые таблицы в базе данных, применив миграции.

```bash
python manage.py migrate
```

### 6. Создание суперпользователя

Создайте суперпользователя для доступа к админке.

```bash
python manage.py createsuperuser
```


Следуйте инструкциям на экране для ввода имени пользователя, электронной почты и пароля.

### 7. Сборка статических файлов

Соберите статические файлы проекта.

```bash
python manage.py collectstatic
```


### 8. Настройка Celery (опционально)

Если в проекте используется Celery для асинхронных задач, необходимо настроить брокер сообщений (например, Redis).

1. Установите Redis:

    - **Ubuntu**:

        ```bash
        sudo apt update
        sudo apt install redis-server
        ```

    - **macOS** (с использованием Homebrew):

        ```bash
        brew install redis
        brew services start redis
        ```

2. Настройте Celery в проекте. Убедитесь, что в `project/settings.py` настроены параметры Celery.
3. Запустите воркер Celery:

    ```bash
    celery -A project worker -l info
    ```

### 9. Запуск сервера разработки

Теперь вы можете запустить сервер разработки Django.

```bash
python manage.py runserver
```


Откройте браузер и перейдите по адресу [http://127.0.0.1:8000/](http://127.0.0.1:8000/) для доступа к проекту.

Для доступа к админ-панели перейдите по адресу [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) и войдите, используя учетные данные суперпользователя.

## Дополнительные настройки

### Настройка переменных окружения

Для безопасности и гибкости рекомендуется использовать переменные окружения для хранения конфиденциальных данных, таких как `SECRET_KEY`, параметры базы данных и другие настройки.

Вы можете использовать библиотеку `python-decouple` для управления переменными окружения.

1. Установите библиотеку:

    ```bash
    pip install python-decouple
    ```

2. Создайте файл `.env` в корне проекта и добавьте необходимые переменные:

    ```env
    SECRET_KEY=ваш_секретный_ключ
    DEBUG=True
    DATABASE_NAME=имя_базы_данных
    DATABASE_USER=ваш_пользователь
    DATABASE_PASSWORD=ваш_пароль
    DATABASE_HOST=localhost
    DATABASE_PORT=5432
    ```

3. Измените `project/settings.py`, чтобы использовать переменные окружения:

    ```python
    from decouple import config

    SECRET_KEY = config('SECRET_KEY')
    DEBUG = config('DEBUG', default=False, cast=bool)

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DATABASE_NAME'),
            'USER': config('DATABASE_USER'),
            'PASSWORD': config('DATABASE_PASSWORD'),
            'HOST': config('DATABASE_HOST'),
            'PORT': config('DATABASE_PORT'),
        }
    }
    ```

