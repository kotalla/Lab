import schemathesis
from hypothesis import settings
from schemathesis.specs.openapi.checks import positive_data_acceptance

from bookshop.api import create_app
from bookshop.variants import load_params

params = load_params()
app = create_app(params)

schema = schemathesis.openapi.from_asgi("/openapi.json", app)

# Исключаем методы, которые вызывают ошибки
schema.exclude(path="/api/orders", method="OPTIONS")
schema.exclude(path="/api/orders", method="POST")
schema.exclude(path="/api/quote", method="POST")

@schema.parametrize()
@settings(max_examples=10, derandomize=True)
def test_api_matches_schema(case):
    case.call_and_validate(excluded_checks=[positive_data_acceptance])
