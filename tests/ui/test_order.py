import pytest
from playwright.sync_api import Page

from tests.ui.pages.catalog_page import CatalogPage
from tests.ui.pages.order_page import OrderPage


def test_create_order_full_flow(page: Page):
    """Сценарий 4: оформление заказа через корзину до статуса NEW."""
    catalog = CatalogPage(page).open()
    catalog.set_book_qty("Евгений Онегин", 1)
    catalog.fill_customer(name="Иван Иванов", email="ivan@example.ru")
    catalog.calculate()
    catalog.submit_order()

    order_page = OrderPage(page)
    order_page.expect_status("NEW")


def test_cancel_order_with_dialog(page: Page):
    """Сценарий 5: создание заказа и последующая отмена через диалог."""
    # Отмечаем как ожидаемо падающий из-за бага #6
    pytest.xfail("Issue #6: Статус заказа не меняется на CANCELLED после отмены")

    catalog = CatalogPage(page).open()
    catalog.set_book_qty("Евгений Онегин", 1)
    catalog.fill_customer(name="Иван Иванов", email="ivan@example.ru")
    catalog.calculate()
    catalog.submit_order()

    order_page = OrderPage(page)
    order_page.expect_status("NEW")
    order_page.cancel_order()
    order_page.expect_status("CANCELLED")
