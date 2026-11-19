GET {{base_url}}/api/books
HTTP 200
[Asserts]
jsonpath "$" count > 0
