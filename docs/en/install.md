# Installation & Launch Guide

## Requirements
- Docker and Docker Compose
- Make
- Python 3.9+ (if running locally, not via Docker)

## Quick Start (Recommended)

1. Clone the repository:
   ```sh
   git clone https://github.com/your-org/online-shop.git
   cd online-shop
   ```
2. Build and start the services:
   ```sh
   make build
   make up
   ```
3. Check that the service is available:
   - API: http://localhost:5005 (or the port specified in docker-compose.yml)

## Running Tests
- All tests:
  ```sh
  make test
  ```
- Unit tests:
  ```sh
  make unit-tests
  ```
- Integration tests:
  ```sh
  make integration-tests
  ```
- E2E tests:
  ```sh
  make e2e-tests
  ```

## Environment Variables
- DB_HOST — database host (default: localhost)
- DB_PASSWORD — database user password (default: abc123)
- API_HOST — API host (default: localhost)

## Manual Launch (without Docker)
1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   pip install -e src
   ```
2. Start Postgres locally and set environment variables.
3. Run the Flask app:
   ```sh
   export FLASK_APP=allocation.entrypoints.flask_app
   export PYTHONPATH=src
   flask run --host=0.0.0.0 --port=5005
   ```

---
[← Back to Table of Contents](index.md)

