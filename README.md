# MemoSpace — Backend API для заметок

## 📌 Описание проекта

MemoSpace — API для управления заметками пользователей.  
Проект разработан как backend-сервис с REST API, позволяющий пользователям создавать, редактировать и удалять заметки, а также хранить их в базе данных с разграничением доступа.

Реализована регистрация и авторизация пользователей с использованием JWT, а также защита данных и бизнес-логика на сервере.

---

## 🚀 Функциональность

- Регистрация и авторизация пользователей (JWT)  
- Разграничение доступа к заметкам: каждый пользователь видит только свои заметки  
- Создание, редактирование, удаление заметок  
- Асинхронное взаимодействие клиента с сервером (AJAX)  
- Валидация пользовательских данных на сервере  
- Хранение данных в реляционной базе данных (MySQL)  
- Миграции базы данных с помощью Alembic  
- Покрытие ключевой бизнес-логики модульными тестами (Pytest)
- Генерация PDF версии заметки (HTML -> PDF через weasyprint)
- Отправка PDF-файла на email пользователя (в виде вложения)

---

## 🏗 Архитектура проекта

- **Backend:** FastAPI  
- **ASGI-сервер:** Uvicorn  
- **ORM:** SQLAlchemy (async)  
- **База данных:** MySQL  
- **Валидация данных:** Pydantic v2  
- **Аутентификация:** JWT  
- **Шаблоны:** Jinja2  
- **Генерация PDF:** WeasyPrint  
- **Email-отправка:** SMTP (smtplib)  
- **Тестирование:** Pytest  
- **Асинхронность:** async/await, asyncio, run_in_executor для блокирующих операций   

---

## 🛠 Используемые технологии

- Python  
- FastAPI  
- SQLAlchemy  
- MySQL  
- JWT  
- Alembic - для миграции базы данных
- Pytest  
- HTML, CSS, JavaScript, jQuery (для асинхронного взаимодействия)  
- RabbitMQ
- Celery, Redis - для выполнения задачи отправки письма на почту в фоновом режиме
- WeasyPrint - для генерации PDF файла

---

## ⚙️ Установка и запуск

### 1. Клонирование репозитория
```bash
git clone https://github.com/AlexGitHub21/MemoSpace.git
cd MemoSpace
````

### 2. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 3. Настройка базы данных
Создать базу данных MySQL
Настроить параметры подключения к БД, указать порт, хост почты/redis в файле .env в корне проекта 
#### 3.1. Создать миграцию
```commandline
alembic revision --autogenerate -m "Create Table"
```
#### 3.2 Примернить миграцию
```commandline
alembic upgrade head
```

### 4. Запуск приложения (не Docker)
В корне проекта прописать команду:
```bash
uvicorn app.apps.main:app --reload
```

### 5. Открыть Swagger UI
http://127.0.0.1:8000/docs


### 6. Запустить RabbitMQ
```commandline
docker compose up -d rabbitmq
```
Ссылка на Habr: https://habr.com/ru/companies/slurm/articles/704208/

### 7. consumer запускаем отдельно
В корне проекта прописываем команду:
```bash
python -m app.rabbitmq.pdf_consumer
```

### 8. Запустить celery
В отдельном терминале в корне проекта:
```commandline
celery -A app.apps.core.celery_app worker -l INFO
```
-l INFO выводит в консоль информационные сообщения о выполняемых процессах

### 8. Запустить redis
``` bash
redis-server 
```
(прописываем команду в терминале в папке проекта)

### 9. Действия с заметками
Действия с заметками доступны только авторизованному пользователю. 
Необходиимо пройти регистрацию, подтвердить почту, авторизоваться и тогда работать с заметками (через Swagger UI)

### Обновление requirements.txt
В проекте используется pip-tools

https://olegtalks.ru/tpost/mlxpblf661-requirementstxt-polnoe-rukovodstvo-po-up

### 10. Запустить через Docker 

***Собрать Docker-образ***
```commandline
docker compose build
```

***Миграция БД***
```
docker compose run --rm app bash
alembic -c alembic.ini revision --autogenerate -m "Initial migration"
alembic -c alembic.ini upgrade head
exit
```

***Запустить контейнеры***
```commandline
docker compose up -d
```

***Запустить consumer***
```commandline
python -m app.rabbitmq.pdf_consumer
```
### 10.1. Просмотреть логи
```commandline
docker compose logs -f worker
```
