# ПРОДУКТОВЫЙ ПОМОЩНИК FOODGRAM

![maste](https://github.com/sabina-045/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg?branch=master)

# Описание

Проект представляет собой API для проекта Foodgram
Развернутый проект можно посмотреть по адресу 'http://158.160.19.39/api/recipes/'
+ Superuser: din
+ Password: mandalor

# FOODGRAM
> - это проект с рецептами пользователей, которые можно добавлять в избранное и список покупок. Список покупок доступен к скачиванию.

### Технологии:
+ Django==4.2.1
+ djangorestframework==3.14.0
+ django-filter==23.2
+ djoser==2.2.0
+ psycopg2-binary==2.9.6
+ gunicorn==20.1.0
+ Docker==20.10.24

#### Как запустить проект, упакованный в контейнер Docker:

+ устанавливаем Docker
'https://www.docker.com/'
+ клонируем репозиторий:
`git clone git@github.com:sabina-045/foodgram-project-react.git`
+ создаем файл `.env` в директории `foodgram/infra/`
    + заполняем его по образцу:
    DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
    DB_NAME=postgres # имя базы данных
    POSTGRES_USER=postgres # логин для подключения к базе данных
    POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
    DB_HOST=localhost # название сервиса (контейнера)
    DB_PORT=5432 # порт для подключения к БД
    SECRET_KEY='n&l%385148polhtyn^##a1)icz@4zqj=rq&agdol^##zgl9(vs' # секретный ключ Django
+ переходим `cd foodgram/infra/`
    + запускаем docker-compose
    `sudo docker-compose up -d`
+ выполняем миграции
`sudo docker-compose exec web python manage.py migrate`
+ создаем суперюзера:
`sudo docker-compose exec web python manage.py createsuperuser`
+ собираем статику:
`sudo docker-compose exec web python manage.py collectstatic --no-input`
+ смотрим проект по адресу http://localhost/
+ для тестирования проекта при желании заливаем данные в базу данных из фикстур:
'sudo docker-compose exec yamdb python manage.py loaddata /foodgram/infra/fixtures.json'

#### Инструкции и примеры

>Основные эндпойнты `api/`:

/recipes/ - список рецептов, добавленных авторизованными пользователями.

/recipes/{recipe_id}/ - информация об отдельном рецепте.

/recipes/{recipe_id}/favorite/ - добавление рецепта в избранное.

/recipes/download_shopping_cart/ - загрузить список покупок.

/users/{user_id}/ - информаци о пользователе со списком его рецептов.

users/subscriptions/ - список подписок пользователя.

</br>

>Для доступа к api необходимо получить токен:

Нужно выполнить POST-запрос http://127.0.0.1:8000/api/auth/token/login/ передав поля username и email.

Полученный токен передаем в заголовке Authorization: token <токен>

</br>
> Команда создателей:
Яндекс Практикум, Сабина Гаджиева

> Вопросы и пожелания по адресу:
sabina_045@mail.ru

