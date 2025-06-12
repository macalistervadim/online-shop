# Архитектура и паттерны

## Архитектурные подходы

Проект построен на принципах Domain-Driven Design (DDD), Clean Architecture и Onion Architecture. Это обеспечивает:
- Чёткое разделение бизнес-логики и инфраструктуры
- Лёгкость тестирования и расширения
- Независимость доменной модели от внешних фреймворков

### DDD (Domain-Driven Design)
- **Доменная модель** (src/allocation/domain/model.py): содержит бизнес-логику, агрегаты (Product), сущности (Batch, OrderLine), value-объекты.
- **Сервисы** (src/allocation/service_layer/services.py): реализуют сценарии использования, оркестрируют работу агрегатов.
- **Репозитории** (src/allocation/adapters/repository.py): абстракция для доступа к данным.
- **UOW (Unit of Work)** (src/allocation/service_layer/unit_of_work.py): управление транзакциями и согласованностью данных.

### Clean Architecture / Onion Architecture
- **Внешний слой**: entrypoints (Flask API)
- **Сервисный слой**: orchestration, бизнес-сценарии
- **Доменный слой**: бизнес-логика, агрегаты, сущности
- **Инфраструктурный слой**: ORM, репозитории, интеграции

### Паттерны
- **Repository** — абстрагирует работу с БД, позволяет подменять реализацию (например, для тестов)
- **Unit of Work** — обеспечивает атомарность операций и управление транзакциями
- **Ports & Adapters (Hexagonal Architecture)** — API и инфраструктура подключаются через абстракции
- **Инверсия зависимостей** — зависимости внедряются через конструкторы и абстракции, а не жёстко прописаны

## Структура каталогов
- **src/allocation/domain/** — доменные модели, бизнес-исключения
- **src/allocation/service_layer/** — сервисы, UOW, сценарии
- **src/allocation/adapters/** — репозитории, ORM-описания
- **src/allocation/entrypoints/** — Flask-приложение (REST API)
- **tests/** — модульные, интеграционные и e2e тесты

## Преимущества выбранной архитектуры
- Масштабируемость и поддерживаемость
- Лёгкость тестирования (TDD)
- Независимость бизнес-логики от инфраструктуры
- Возможность быстрой замены технологий хранения данных или API

## Диаграмма слоёв

```
[ API (Flask) ]
      ↓
[ Service Layer ]
      ↓
[ Domain Model ]
      ↓
[ Infrastructure (ORM, DB) ]
```

## Подробнее о паттернах
- **Repository**: src/allocation/adapters/repository.py
- **Unit of Work**: src/allocation/service_layer/unit_of_work.py
- **Сервисы**: src/allocation/service_layer/services.py
- **Модели**: src/allocation/domain/model.py

---

[← Назад к оглавлению](../index.md)

