# REST API

## Базовый URL

- По умолчанию: `http://localhost:5005`
- В Docker: порт может быть переопределён в `docker-compose.yml`

---

## POST /allocate

**Назначение:** разместить позицию заказа в партии товара.

**Пример запроса:**
```json
POST /allocate
{
  "orderid": "order-123",
  "sku": "CHAIR-RED",
  "qty": 10
}
```

**Пример успешного ответа:**
```json
{
  "batchref": "batch-001"
}
```

**Ошибки:**
- 400, если товара нет в наличии или неверный SKU

---

## POST /add_batch

**Назначение:** добавить новую партию товара.

**Пример запроса:**
```json
POST /add_batch
{
  "ref": "batch-001",
  "sku": "CHAIR-RED",
  "qty": 100,
  "eta": "2025-06-12"  // или null, если партия на складе
}
```

**Пример успешного ответа:**
```
OK
```

---

## Примечания
- Все запросы и ответы — в формате JSON
- Для тестирования удобно использовать Postman или curl
- Для расширения API добавляйте новые endpoint'ы в `src/allocation/entrypoints/flask_app.py`

---
[← Назад к оглавлению](../index.md)

