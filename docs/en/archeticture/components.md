# Architecture & Patterns

## Architectural Approaches

The project is based on Domain-Driven Design (DDD), Clean Architecture, and Onion Architecture principles. This ensures:
- Clear separation of business logic and infrastructure
- Easy testing and extension
- Domain model independence from frameworks

### DDD (Domain-Driven Design)
- **Domain Model** (`src/allocation/domain/model.py`): contains business logic, aggregates (Product), entities (Batch, OrderLine), value objects
- **Services** (`src/allocation/service_layer/services.py`): implement use cases, orchestrate aggregates
- **Repositories** (`src/allocation/adapters/repository.py`): abstraction for data access
- **UOW (Unit of Work)** (`src/allocation/service_layer/unit_of_work.py`): transaction and consistency management

### Clean Architecture / Onion Architecture
- **Outer layer**: entrypoints (Flask API)
- **Service layer**: orchestration, business scenarios
- **Domain layer**: business logic, aggregates, entities
- **Infrastructure layer**: ORM, repositories, integrations

### Patterns
- **Repository** — abstracts DB access, allows easy replacement (e.g., for tests)
- **Unit of Work** — ensures atomicity and transaction management
- **Ports & Adapters (Hexagonal Architecture)** — API and infrastructure are connected via abstractions
- **Dependency Inversion** — dependencies are injected via constructors and abstractions, not hardcoded

## Directory Structure
- **src/allocation/domain/** — domain models, business exceptions
- **src/allocation/service_layer/** — services, UOW, use cases
- **src/allocation/adapters/** — repositories, ORM mappings
- **src/allocation/entrypoints/** — Flask app (REST API)
- **tests/** — unit, integration, and e2e tests

## Advantages of the Architecture
- Scalability and maintainability
- Easy testing (TDD)
- Business logic independence from infrastructure
- Fast technology or API replacement

## Layer Diagram

```
[ API (Flask) ]
      ↓
[ Service Layer ]
      ↓
[ Domain Model ]
      ↓
[ Infrastructure (ORM, DB) ]
```

## More on Patterns
- **Repository**: src/allocation/adapters/repository.py
- **Unit of Work**: src/allocation/service_layer/unit_of_work.py
- **Services**: src/allocation/service_layer/services.py
- **Models**: src/allocation/domain/model.py

---

[← Back to Table of Contents](../index.md)

