POST {{base_url}}/api/quote
Content-Type: application/json
{
  "items": [{"book_id": 1, "qty": 1}],
  "delivery": "courier"
}

HTTP 200
[Asserts]
jsonpath "$.delivery_cost" == 199.0

# 2. Бесплатная доставка (на пороге 2000+ руб)
POST {{base_url}}/api/quote
Content-Type: application/json
{
  "items": [{"book_id": 1, "qty": 4}],
  "delivery": "courier"
}

HTTP 200
[Asserts]
jsonpath "$.delivery_cost" == 0.0