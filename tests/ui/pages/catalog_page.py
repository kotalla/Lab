from playwright.sync_api import Page, expect


class CatalogPage:
    def __init__(self, page: Page):
        self.page = page
        self.rows = page.get_by_test_id("book-row")
        self.calculate_button = page.get_by_role("button", name="Рассчитать")
        self.submit_button = page.get_by_role("button", name="Оформить заказ")
        self.total = page.get_by_test_id("total")

        # Поля формы покупателя
        self.customer_name = page.get_by_label("Имя")
        self.customer_email = page.get_by_label("Электронная почта")
        self.delivery_courier = page.get_by_role("radio", name="Курьер")
        self.delivery_pickup = page.get_by_role("radio", name="Самовывоз")
        self.promo_input = page.get_by_label("Промокод")

        # Локатор блока ошибки по роли alert (без XPath)
        self.error_alert = page.get_by_role("alert")

    def open(self) -> "CatalogPage":
        self.page.goto("/")
        expect(self.rows.first).to_be_visible()
        return self

    def set_book_qty(self, title: str, qty: int) -> "CatalogPage":
        self.page.get_by_label(f"Количество: {title}").fill(str(qty))
        return self

    def calculate(self) -> "CatalogPage":
        self.calculate_button.click()
        return self

    def fill_customer(self, name: str, email: str) -> "CatalogPage":
        self.customer_name.fill(name)
        self.customer_email.fill(email)
        return self

    def submit_order(self) -> None:
        self.submit_button.click()

    def expect_calculate_button_enabled(self) -> None:
        expect(self.calculate_button).to_be_enabled()

    def expect_total_contains(self, text: str) -> None:
        expect(self.total).to_be_visible()
        expect(self.total).to_contain_text(text)

    def expect_error_visible(self) -> None:
        expect(self.error_alert).to_be_visible()
        expect(self.error_alert).to_contain_text(
        "Выберите хотя бы одну книгу"
    )

