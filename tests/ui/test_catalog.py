from playwright.sync_api import Page

from tests.ui.pages.catalog_page import CatalogPage


def test_smoke_catalog_loads(page: Page):
    """Сценарий 1 (Smoke): страница открывается, кнопка расчета активна."""
    catalog = CatalogPage(page).open()
    catalog.expect_calculate_button_enabled()


def test_calculate_quote_with_items(page: Page):
    """Сценарий 2: добавление книги, расчет стоимости."""
    catalog = CatalogPage(page).open()
    catalog.set_book_qty("Евгений Онегин", 1)
    catalog.calculate()
    catalog.expect_total_contains("₽")


def test_calculate_empty_cart_shows_error(page: Page):
    """Сценарий 3: расчет с нулевым количеством вызывает алерт ошибки."""
    catalog = CatalogPage(page).open()
    catalog.calculate()
    catalog.expect_error_visible()
