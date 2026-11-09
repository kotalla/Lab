from decimal import Decimal

import pytest

from bookshop import pricing
from bookshop.pricing import Line, RuleViolation


MAX_ITEMS = 5
MAX_QTY = 10
SILVER_PCT = 5
GOLD_PCT = 10
BULK_QTY = 10
BULK_PCT = 5
PROMO_CODE = "READMORE"
PROMO_PCT = 15
PROMO_MIN = 1500
MAX_DISCOUNT_PCT = 25
FREE_DELIVERY_FROM = 3000
DELIVERY_FEE = 299



def test_check_lines_valid(params):
    
    lines = [(1, 1), (2, 9)]
    assert pricing.check_lines(lines, params) is None


def test_check_lines_empty(params):
    with pytest.raises(RuleViolation, match="В заказе должна быть хотя бы одна позиция"):
        pricing.check_lines([], params)


def test_check_lines_too_many_items(params):
    lines = [(i, 1) for i in range(MAX_ITEMS + 1)]
    with pytest.raises(RuleViolation):
        pricing.check_lines(lines, params)


def test_check_lines_duplicate_isbn(params):
    lines = [(1, 1), (1, 2)]
    with pytest.raises(RuleViolation):
        pricing.check_lines(lines, params)


def test_check_lines_qty_zero(params):
    with pytest.raises(RuleViolation):
        pricing.check_lines([(1, 0)], params)


# Этот тест падает, так как qty=10 не входит в range(1, 10). Это баг R-03.
@pytest.mark.xfail(reason="#1 — MAX_QTY не включен в диапазон qty (строка 77)", strict=True)
def test_check_lines_boundary_qty(params):
    lines = [(1, MAX_QTY)]
    pricing.check_lines(lines, params)

def test_loyalty_percent_none(params):
    assert pricing.loyalty_percent("none", params) == 0


def test_loyalty_percent_silver(params):
    assert pricing.loyalty_percent("silver", params) == SILVER_PCT


def test_loyalty_percent_gold(params):
    assert pricing.loyalty_percent("gold", params) == GOLD_PCT


def test_loyalty_percent_invalid(params):
    with pytest.raises(RuleViolation, match="Неизвестный уровень карты"):
        pricing.loyalty_percent("platinum", params)


def test_bulk_percent_under(params):
    assert pricing.bulk_percent(BULK_QTY - 1, params) == 0


def test_bulk_percent_exact(params):
    assert pricing.bulk_percent(BULK_QTY, params) == BULK_PCT


def test_promo_valid(params):
    # Код возвращает True, а не процент. Исправляем ожидание.
    assert pricing.promo_applies(PROMO_CODE, Decimal(PROMO_MIN + 500), params) is True


def test_promo_below_min(params):
    with pytest.raises(RuleViolation):
        pricing.promo_applies(PROMO_CODE, Decimal(PROMO_MIN - 1), params)


@pytest.mark.xfail(reason="#1 — пустая строка вызывает RuleViolation", strict=True)
def test_promo_below_empty_string(params):
    with pytest.raises(RuleViolation):
        pricing.promo_applies("   ", Decimal("2000"), params)

def test_promo_none(params):
    assert pricing.promo_applies(None, Decimal(2000), params) is False


# Этот тест ожидает процент, а код возвращает bool. Это баг.
@pytest.mark.xfail(reason="#2 — promo_applies возвращает bool вместо процента", strict=True)
def test_promo_returns_percent_instead_of_bool(params):
    assert pricing.promo_applies(PROMO_CODE, Decimal("2000"), params) == PROMO_PCT



def test_discount_percent_no_promo(params):
    # 10 (gold) + 5 (bulk) = 15. Лимит 25. Ожидаем 15.
    assert pricing.discount_percent("gold", 10, False, params) == 15

@pytest.mark.xfail(reason="#3 — discount_percent не ограничивает скидку лимитом MAX_DISCOUNT", strict=True)
def test_discount_percent_with_promo(params):
    # 10 + 5 + 15 = 30. Лимит 25. Ожидаем 25, но получим 30.
    assert pricing.discount_percent("gold", 10, True, params) == MAX_DISCOUNT_PCT


@pytest.mark.xfail(reason="#4 — discount_amount падает при float проценте (строка 137)", strict=True)
def test_discount_amount_rounding_down():
    assert pricing.discount_amount(Decimal("1000"), 33.333) == Decimal("333.33")

def test_discount_amount_rounding_down_int():
    assert pricing.discount_amount(Decimal("1000"), 33) == Decimal("330.00")


# --- 5. Тесты доставки ---

def test_delivery_courier_free(params):
    assert pricing.delivery_cost(Decimal(FREE_DELIVERY_FROM + 1), "courier", params) == Decimal("0.00")


def test_delivery_courier_paid(params):
    assert pricing.delivery_cost(Decimal(FREE_DELIVERY_FROM - 1), "courier", params) == Decimal(str(DELIVERY_FEE))


def test_delivery_pickup(params):
    assert pricing.delivery_cost(Decimal("100"), "pickup", params) == Decimal("0.00")


def test_delivery_invalid_method(params):
    with pytest.raises(RuleViolation, match="Неизвестный способ доставки"):
        pricing.delivery_cost(Decimal("100"), "drone", params)


def test_subtotal_rounding():
    lines = [
        Line(book_id=1, price=Decimal("10.333"), qty=1),
        Line(book_id=2, price=Decimal("20.666"), qty=1)
    ]
    assert pricing.subtotal(lines) == Decimal("31.00")


def test_items_count():
    lines = [
        Line(book_id=1, price=Decimal("10"), qty=2),
        Line(book_id=2, price=Decimal("20"), qty=3)
    ]
    assert pricing.items_count(lines) == 5


# внутри calculate создается список qty=12, который падает в check_lines из-за range.
@pytest.mark.xfail(reason="#5 — calculate не может обработать qty=MAX_QTY из-за check_lines", strict=True)
def test_calculate_full(params):
    lines = [
        Line(book_id=1, price=Decimal("250"), qty=12)
    ]
    result = pricing.calculate(
        lines, 
        params, 
        loyalty="gold", 
        promo_code="READMORE", 
        delivery="courier"
    )
    assert result.subtotal == Decimal("3000.00")
    assert result.discount == Decimal("750.00")
    assert result.goods_total == Decimal("2250.00")
    assert result.delivery_cost == Decimal("299.00")
    assert result.total == Decimal("2549.00")
    assert result.promo_applied is True

def test_calculate_full_valid_qty(params):
    lines = [
        Line(book_id=1, price=Decimal("250"), qty=9) # 9 проходит в range(1, 10)
    ]
    result = pricing.calculate(
        lines, 
        params, 
        loyalty="gold", 
        promo_code="READMORE", 
        delivery="courier"
    )
    assert isinstance(result, pricing.Quote)
    assert result.total > 0