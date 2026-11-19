POST {{base_url}}/api/orders
Content-Type: application/json

{
  "customer": {
    "name": "Тест",
    "email": "test@lab.ru"
  },
  "items": [
    {
      "book_id": 1,
      "qty": 11
    }
  ]
}

HTTP 422

[Asserts]
jsonpath "$.detail[0].loc[0]" == "body"
jsonpath "$.detail[0].loc[1]" == "qty"