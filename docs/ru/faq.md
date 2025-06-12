# FAQ (Часто задаваемые вопросы)

## 1. Какой стек используется в проекте?
- Python 3.9+
- Flask (REST API)
- SQLAlchemy (ORM)
- PostgreSQL (БД)
- Docker, Docker Compose
- Makefile для автоматизации
- Pytest для тестирования

## 2. Как устроена архитектура?
- Используются DDD, Clean Architecture, Onion Architecture
- Слои: entrypoints (API), service_layer (сервисы, UOW), domain (модели), adapters (репозитории, ORM)
- Паттерны: Repository, Unit of Work, Ports & Adapters, инверсия зависимостей

## 3. Как быстро развернуть проект?
- Используйте команды make build и make up
- Все тесты: make test
- Подробно — см. [гайд по установке](install.md)

## 4. Как добавить новый endpoint в API?
- Добавьте функцию-обработчик в src/allocation/entrypoints/flask_app.py
- Зарегистрируйте новый маршрут через @app.route
- Опишите новый endpoint в документации (docs/ru/api/rest.md)

## 5. Как писать тесты?
- Тесты лежат в tests/unit, tests/integration, tests/e2e
- Используйте Pytest
- Для unit-тестов можно мокать репозитории и UOW

## 6. Как работает миграция схемы БД?
- Схема описана в src/allocation/adapters/orm.py
- Для миграций рекомендуется использовать Alembic (не входит в поставку по умолчанию)

## 7. Как расширять доменную модель?
- Добавляйте новые сущности/агрегаты в src/allocation/domain/model.py
- Описывайте бизнес-логику в доменных моделях
- Используйте сервисы для оркестрации сценариев

## 8. Как настроить переменные окружения?
- Все переменные описаны в src/allocation/config.py
- Можно задавать через .env или напрямую в docker-compose.yml

## 9. Какой порядок онбординга нового разработчика?
1. Прочитать документацию (index, install, architecture)
2. Развернуть проект локально
3. Ознакомиться с тестами и бизнес-логикой
4. Попробовать добавить тест или endpoint

---
[← Назад к оглавлению](index.md)

