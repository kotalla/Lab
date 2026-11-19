import pytest
from decimal import Decimal

from hypothesis import given, settings, strategies as st

from bookshop import pricing
from bookshop.pricing import Line, RuleViolation


# BVA: доставка
@pytest.mark.parametrize(
    ("goods_total", "expected_cost"),
    [
        pytest.param(
            Decimal("2999.99"),
            Decimal("299.00"),
            marks=pytest.mark.tc("TC-002"),
            id="paid",
        ),
        pytest.param(
            Decimal("2000.00"),
            Decimal("0.00"),
            marks=pytest.mark.tc("TC-001"),
            id="free",
        ),
        pytest.param(
            Decimal("3000.01"),
            Decimal("0.00"),
            marks=pytest.mark.tc("TC-003"),
            id="above",
        ),
    ],
)
def test_free_delivery_boundary(params, goods_total, expected_cost):
    assert pricing.delivery_cost(
        goods_total,
        "courier",
        params,
    ) == expected_cost


# DT: таблица решений по скидкам
@pytest.mark.parametrize(
    ("loyalty", "bulk", "promo", "expected_pct"),
    [
        pytest.param(
            "gold",
            True,
            True,
            27,
            marks=[
                pytest.mark.tc("TC-004"),
                pytest.mark.xfail(
                    strict=True,
                    reason="Issue #2: скидка превышает максимальный лимит",
                ),
            ],
            id="dt_gold_all",
        ),
        pytest.param(
            "none",
            False,
            True,
            15,
            marks=pytest.mark.tc("TC-005"),
            id="dt_none_promo",
        ),
        pytest.param(
            "silver",
            False,
            True,
            19,
            marks=pytest.mark.tc("TC-010"),
            id="dt_silver_promo",
        ),
        pytest.param(
            "silver",
            True,
            False,
            12,
            marks=pytest.mark.tc("TC-011"),
            id="dt_silver_bulk",
        ),
        pytest.param(
            "gold",
            True,
            False,
            17,
            marks=pytest.mark.tc("TC-012"),
            id="dt_gold_bulk",
        ),
    ],
)
def test_discount_decision_table(
    params,
    loyalty,
    bulk,
    promo,
    expected_pct,
):
    count = params.bulk_qty if bulk else 1

    result = pricing.discount_percent(
        loyalty,
        count,
        promo,
        params,
    )

    assert result == expected_pct


# EP: классы промокодов
@pytest.mark.parametrize(
    ("promo", "expected"),
    [
        pytest.param(
            "WRONG",
            RuleViolation,
            marks=pytest.mark.tc("TC-003"),
            id="ep_unknown",
        ),
        pytest.param(
    "   ",
    False,
    marks=pytest.mark.tc("TC-018"),
    id="ep_empty",
),
        pytest.param(
            None,
            False,
            marks=pytest.mark.tc("TC-016"),
            id="ep_none",
        ),
    ],
)
def test_promo_equivalence_classes(params, promo, expected):
    if expected == RuleViolation:
        with pytest.raises(RuleViolation):
            pricing.promo_applies(
                promo,
                Decimal("2000"),
                params,
            )
    else:
        assert pricing.promo_applies(
            promo,
            Decimal("2000"),
            params,
        ) is expected


# Hypothesis: проверка формулы итоговой суммы
prices = st.decimals(
    min_value=Decimal("1.00"),
    max_value=Decimal("5000.00"),
    places=2,
    allow_nan=False,
    allow_infinity=False,
)

qtys = st.integers(
    min_value=1,
    max_value=10,
)


@settings(
    max_examples=200,
    derandomize=True,
)
@given(
    price=prices,
    qty=qtys,
)
def test_total_consistency_property(params, price, qty):
    lines = [
        Line(
            book_id=1,
            price=price,
            qty=qty,
        )
    ]

    quote = pricing.calculate(
        lines,
        params,
        delivery="courier",
    )

    assert quote.total == (
        quote.subtotal
        - quote.discount
        + quote.delivery_cost
    )
    from hypothesis import given, settings, strategies as st


@pytest.mark.tc("TC-004")
@pytest.mark.xfail(
    strict=True,
    reason="Issue #2: скидка после промокода превышает MAX_DISCOUNT_PCT",
)
@settings(max_examples=200, derandomize=True)
@given(
    loyalty=st.sampled_from(["none", "silver", "gold"]),
    count=st.integers(min_value=1, max_value=20),
    promo=st.booleans(),
)
def test_discount_never_exceeds_maximum(params, loyalty, count, promo):
    """
    R-09: итоговая скидка не может быть больше установленного максимума.
    """
    result = pricing.discount_percent(
        loyalty=loyalty,
        count=count,
        promo=promo,
        params=params,
    )

    assert 0 <= result <= params.max_discount_pct