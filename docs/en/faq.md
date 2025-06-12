# FAQ (Frequently Asked Questions)

## 1. What tech stack is used in the project?
- Python 3.9+
- Flask (REST API)
- SQLAlchemy (ORM)
- PostgreSQL (DB)
- Docker, Docker Compose
- Makefile for automation
- Pytest for testing

## 2. How is the architecture organized?
- DDD, Clean Architecture, Onion Architecture
- Layers: entrypoints (API), service_layer (services, UOW), domain (models), adapters (repositories, ORM)
- Patterns: Repository, Unit of Work, Ports & Adapters, Dependency Inversion

## 3. How to quickly run the project?
- Use make build and make up
- All tests: make test
- See [installation guide](install.md) for details

## 4. How to add a new API endpoint?
- Add a handler function in src/allocation/entrypoints/flask_app.py
- Register a new route with @app.route
- Document the new endpoint in docs/en/api/rest.md

## 5. How to write tests?
- Tests are in tests/unit, tests/integration, tests/e2e
- Use Pytest
- For unit tests, you can mock repositories and UOW

## 6. How is DB schema migration handled?
- Schema is defined in src/allocation/adapters/orm.py
- For migrations, use Alembic (not included by default)

## 7. How to extend the domain model?
- Add new entities/aggregates in src/allocation/domain/model.py
- Implement business logic in domain models
- Use services for orchestration

## 8. How to configure environment variables?
- All variables are described in src/allocation/config.py
- Set them via .env or directly in docker-compose.yml

## 9. What is the onboarding process for a new developer?
1. Read the documentation (index, install, architecture)
2. Run the project locally
3. Review tests and business logic
4. Try adding a test or endpoint

---
[← Back to Table of Contents](index.md)

