POST {{base_url}}/api/orders
{
  "customer": {"name": "Борис", "email": "boris@lab.ru"},
  "items": [{"book_id": 4, "qty": 1}]
}
HTTP 201
[Captures]
order_id: jsonpath "$.id"

POST {{base_url}}/api/orders/{{order_id}}/pay
HTTP 200
[Asserts]
jsonpath "$.status" == "PAID"

# Проверяем, что GET возвращает новый статус
GET {{base_url}}/api/orders/{{order_id}}
HTTP 200
[Asserts]
jsonpath "$.status" == "PAID"