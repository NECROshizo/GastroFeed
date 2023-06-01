# Проект Foodgram
## Технологии
[![Python](https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=56C0C0&color=gray)](https://www.python.org/) [![Django](https://img.shields.io/badge/-Django-464646?style=flat&logo=Django&logoColor=56C0C0&color=gray)](https://www.djangoproject.com/) [![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat&logo=Django%20REST%20Framework&logoColor=56C0C0&color=gray)](https://www.django-rest-framework.org/) [![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat&logo=PostgreSQL&logoColor=56C0C0&color=gray)](https://www.postgresql.org/) [![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat&logo=NGINX&logoColor=56C0C0&color=gray)](https://nginx.org/ru/) [![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat&logo=gunicorn&logoColor=56C0C0&color=gray)](https://gunicorn.org/) [![Docker](https://img.shields.io/badge/-Docker-464646?style=flat&logo=Docker&logoColor=56C0C0&color=gray)](https://www.docker.com/) [![Docker-compose](https://img.shields.io/badge/-Docker%20compose-464646?style=flat&logo=Docker&logoColor=56C0C0&color=gray)](https://www.docker.com/) [![Docker Hub](https://img.shields.io/badge/-Docker%20Hub-464646?style=flat&logo=Docker&logoColor=56C0C0&color=gray)](https://www.docker.com/products/docker-hub)
##### Полный список модулей, используемых в проекте, доступен в [requirements.txt](https://github.com/NECROshizo/foodgram-project-react/blob/master/backend/requirements.txt)
## Линтеры
[![Flake8](https://img.shields.io/badge/-flake8-464646?style=flat&logo=flake8&logoColor=56C0C0&color=gray)](https://flake8.pycqa.org/)
## Статус CI/CD
![Workflow](https://github.com/NECROshizo/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

## Описание проекта
Cайт Foodgram, «Продуктовый помощник». Онлайн-сервис и API. На этом сервисе пользователи смогут:
- публиковать рецепты и редоктировать свои,
- подписываться на публикации других пользователей, 
- добавлять понравившиеся рецепты в список «Избранное», 
- а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Установка и настройки из контейнера Docker
#### Запуск сборки из файл docker-compose.yaml:

```
cd foodgram-project-reac/infra
docker-compose up -d
```
**При необходимости пересборки контейнера:**
```
docker-compose up -d --build
```
#### Создание и применение миграции:
```
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
```
#### Создание суперпользовотеля:
```
docker-compose exec backend python manage.py createsuperuser
```
#### Сбор статистики:
```
docker-compose exec backend python manage.py collectstatic --no-input
```
#### Импорт данных в базу данных::
```
docker-compose exec backend python manage.py loaddata data.json
```
#### Проект для демонстрации
Проект можно посмотреть по адрессу [fodgram](http://84.201.176.35)
#### Настройка параметров допуска оуружения к базе данных
```
touch .env
```
Шаблон файла **.env**
```
SECRET_KEY=<секретный ключ Django>
DEBUG=<Включение отключение функции отладки>
DB_ENGINE=django.db.backends.postgresql
DB_NAME=<имя БД>
POSTGRES_USER=<Имя пользователя>
POSTGRES_PASSWORD=<пароль>
DB_HOST=<хост БД>
DB_PORT=<порт для допуска к БД>
```
## Автор
[**Оганин Пётр**](https://github.com/NECROshizo) 
2023 г.
