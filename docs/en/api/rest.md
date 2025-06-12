# REST API

## Base URL

- Default: `http://localhost:5005`
- In Docker: the port may be overridden in `docker-compose.yml`

---

## POST /allocate

**Purpose:** Allocate an order line to a product batch.

**Sample request:**
```json
POST /allocate
{
  "orderid": "order-123",
  "sku": "CHAIR-RED",
  "qty": 10
}
```

**Sample successful response:**
```json
{
  "batchref": "batch-001"
}
```

**Errors:**
- 400, if the product is out of stock or SKU is invalid

---

## POST /add_batch

**Purpose:** Add a new product batch.

**Sample request:**
```json
POST /add_batch
{
  "ref": "batch-001",
  "sku": "CHAIR-RED",
  "qty": 100,
  "eta": "2025-06-12"  // or null if the batch is in stock
}
```

**Sample successful response:**
```
OK
```

---

## Notes
- All requests and responses are in JSON format
- Use Postman or curl for testing
- To extend the API, add new endpoints in `src/allocation/entrypoints/flask_app.py`

---
[← Back to Table of Contents](../index.md)

