# Установка и запуск

## Требования
- Docker и Docker Compose
- Make
- Python 3.9+ (если запускать локально, не через Docker)

## Быстрый старт (рекомендуется)

1. Клонируйте репозиторий:
   ```sh
   git clone https://github.com/your-org/online-shop.git
   cd online-shop
   ```
2. Соберите и запустите сервисы:
   ```sh
   make build
   make up
   ```
3. Проверьте, что сервис доступен:
   - API: http://localhost:5005 (или порт, указанный в docker-compose.yml)

## Запуск тестов
- Все тесты:
  ```sh
  make test
  ```
- Модульные тесты:
  ```sh
  make unit-tests
  ```
- Интеграционные тесты:
  ```sh
  make integration-tests
  ```
- E2E тесты:
  ```sh
  make e2e-tests
  ```

## Переменные окружения
- DB_HOST — адрес базы данных (по умолчанию: localhost)
- DB_PASSWORD — пароль пользователя БД (по умолчанию: abc123)
- API_HOST — адрес API (по умолчанию: localhost)

## Ручной запуск (без Docker)
1. Установите зависимости:
   ```sh
   pip install -r requirements.txt
   pip install -e src
   ```
2. Запустите Postgres локально и настройте переменные окружения.
3. Запустите Flask-приложение:
   ```sh
   export FLASK_APP=allocation.entrypoints.flask_app
   export PYTHONPATH=src
   flask run --host=0.0.0.0 --port=5005
   ```

---
[← Назад к оглавлению](index.md)

