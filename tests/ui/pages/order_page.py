from playwright.sync_api import Page, expect


class OrderPage:
    def __init__(self, page: Page):
        self.page = page
        self.order_status = page.get_by_test_id("order-status")
        self.pay_button = page.get_by_role("button", name="Оплатить")
        self.cancel_button = page.get_by_role("button", name="Отменить")

    def open(self, order_id: int | str) -> "OrderPage":
        self.page.goto(f"/orders/{order_id}")
        expect(self.order_status).to_be_visible()
        return self

    def pay_order(self) -> "OrderPage":
        self.pay_button.click()
        return self

    def cancel_order(self) -> "OrderPage":
        # Перехватываем системный alert/confirm диалог подтверждения отмены
        self.page.once("dialog", lambda dialog: dialog.accept())
        # Нажимаем кнопку отмены без expect_navigation, так как обновление происходит через AJAX
        self.cancel_button.click()
        return self

    def expect_status(self, expected_status: str) -> None:
        # Проверяем атрибут data-status (NEW, PAID, CANCELLED и т.д.)
        expect(self.order_status).to_have_attribute("data-status", expected_status)
