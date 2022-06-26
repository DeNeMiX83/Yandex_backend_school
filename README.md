# Docker

Перед запуском следует обновить конфиг в `backend\prod.env`, `prod.env`, `nginx\default.conf` указав там данные описанные в
`backend\example.env`, `example.env`, `nginx\example.conf`

В `docker-compose.prod.yml`  поменять внешние порты для контейнеров.

Для запуска контейнеров: `docker-compose -f docker-compose.prod.yml up`
# Структура

`backend` - реализация REST API.

Содержит в себе:

* `apps` - описание приложений. Каждое приложение содержит `urls` - endpoints, `serializers` - работа с json и ORM моделями БД, `models` - описание ORM моделей.
* `configs` - настройка сервера API.

`nginx` - для работы то static файлами.

# Принцип работы

Docker создает контейнеры:
* `db` - база данных PostgreSQL, `порт: 5432`
* `backend` - сервер API, `порт: 8000`
* `nginx` - сервер nginx, отдает статику по `url /static` и проксирует запросы на `backend`, `порт: 80`

