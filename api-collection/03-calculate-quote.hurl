POST {{base_url}}/api/quote
Content-Type: application/json

{
  "items": [
    {
      "book_id": 1,
      "qty": 1
    }
  ],
  "loyalty": "none",
  "delivery": "pickup"
}

HTTP 200

[Asserts]
jsonpath "$.total" isNumber
