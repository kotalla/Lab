POST {{base_url}}/api/quote
{
  "items": [{"book_id": 1, "qty": 1}],
  "promo_code": "WRONGCODE"
}
HTTP 422
[Asserts]
# Ожидаем ошибку бизнес-логики
jsonpath "$.detail[0].type" == "business_rule"