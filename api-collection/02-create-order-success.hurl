POST {{base_url}}/api/orders
Content-Type: application/json
{
  "customer": {"name": "Анна", "email": "anna@example.ru"},
  "items": [
    {"book_id": 1, "qty": 2},
    {"book_id": 2, "qty": 1}
  ]
}
HTTP 201

[Captures]
order_id: jsonpath "$.id"

GET {{base_url}}/api/orders/{{order_id}}
HTTP 200

[Asserts]
jsonpath "$.status" == "NEW"
jsonpath "$.lines" count == 2
