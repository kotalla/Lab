import pytest

# Константа клиента должна быть определена в conftest.py или здесь
CUSTOMER = {"name": "Анна", "email": "anna@example.ru"}

# --- Позитивные сценарии (вызывают все основные эндпоинты) ---

def test_health_check(client):
    """Проверка доступности сервиса (Smoke). Эндпоинт: GET /api/health"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_get_catalog(client):
    """Получение списка книг. Эндпоинт: GET /api/books"""
    response = client.get("/api/books")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "title" in data[0]

def test_get_specific_book(client):
    """Получение конкретной книги. Эндпоинт: GET /api/books/1"""
    response = client.get("/api/books/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_create_order_and_check_stock(client):
    """Создание заказа и проверка побочного эффекта (остаток). Эндпоинты: POST /api/orders, GET /api/books/1"""
    # Запоминаем остаток до заказа
    stock_before = client.get("/api/books/1").json()["stock"]
    
    body = {"customer": CUSTOMER, "items": [{"book_id": 1, "qty": 2}]}
    response = client.post("/api/orders", json=body)
    
    assert response.status_code == 201
    assert response.json()["status"] == "NEW"
    
    # Проверяем побочный эффект: остаток уменьшился
    stock_after = client.get("/api/books/1").json()["stock"]
    assert stock_after == stock_before - 2

def test_get_orders_list(client):
    """Получение списка заказов. Эндпоинт: GET /api/orders"""
    # Сначала создаем заказ, чтобы список не был пустым
    client.post("/api/orders", json={"customer": CUSTOMER, "items": [{"book_id": 1, "qty": 1}]})
    
    response = client.get("/api/orders")
    assert response.status_code == 200
    assert len(response.json()) >= 1

def test_get_order_by_id(client):
    """Получение деталей заказа. Эндпоинт: GET /api/orders/{id}"""
    order_resp = client.post("/api/orders", json={"customer": CUSTOMER, "items": [{"book_id": 1, "qty": 1}]})
    order_id = order_resp.json()["id"]
    
    response = client.get(f"/api/orders/{order_id}")
    assert response.status_code == 200
    assert response.json()["id"] == order_id

def test_pay_order(client):
    """Оплата заказа. Эндпоинт: POST /api/orders/{id}/pay"""
    order_resp = client.post("/api/orders", json={"customer": CUSTOMER, "items": [{"book_id": 1, "qty": 1}]})
    order_id = order_resp.json()["id"]
    
    response = client.post(f"/api/orders/{order_id}/pay")
    assert response.status_code == 200
    assert response.json()["status"] == "PAID"

def test_ship_order(client):
    """Отгрузка заказа. Эндпоинт: POST /api/orders/{id}/ship"""
    order_resp = client.post("/api/orders", json={"customer": CUSTOMER, "items": [{"book_id": 1, "qty": 1}]})
    order_id = order_resp.json()["id"]
    client.post(f"/api/orders/{order_id}/pay") # Сначала платим
    
    response = client.post(f"/api/orders/{order_id}/ship")
    assert response.status_code == 200
    assert response.json()["status"] == "SHIPPED"

def test_deliver_order(client):
    """Доставка заказа. Эндпоинт: POST /api/orders/{id}/deliver"""
    order_resp = client.post("/api/orders", json={"customer": CUSTOMER, "items": [{"book_id": 1, "qty": 1}]})
    order_id = order_resp.json()["id"]
    client.post(f"/api/orders/{order_id}/pay")
    client.post(f"/api/orders/{order_id}/ship")
    
    response = client.post(f"/api/orders/{order_id}/deliver")
    assert response.status_code == 200
    assert response.json()["status"] == "DELIVERED"

    
def test_get_variant(client):
    """GET /api/variant"""
    response = client.get("/api/variant")
    assert response.status_code == 200

def test_return_order(client):
    """POST /api/orders/{id}/return"""
    # Сначала создаем, оплачиваем и доставляем (иначе нельзя вернуть)
    order = client.post("/api/orders", json={"customer": CUSTOMER, "items": [{"book_id": 1, "qty": 1}]}).json()
    client.post(f"/api/orders/{order['id']}/pay")
    client.post(f"/api/orders/{order['id']}/ship")
    client.post(f"/api/orders/{order['id']}/deliver")
    
    response = client.post(f"/api/orders/{order['id']}/return")
    assert response.status_code == 200

# --- Негативные сценарии (маркер @pytest.mark.negative) ---

@pytest.mark.negative
def test_get_unknown_order_is_404(client):
    """Запрос несуществующего заказа. Эндпоинт: GET /api/orders/999"""
    response = client.get("/api/orders/999")
    assert response.status_code == 404

@pytest.mark.negative
def test_create_order_with_invalid_book_id(client):
    body = {"customer": CUSTOMER, "items": [{"book_id": 99999, "qty": 1}]}
    response = client.post("/api/orders", json=body)
    # Попробуй принять 404, если книга не найдена, или 422
    assert response.status_code in [404, 422]


@pytest.mark.negative
def test_create_order_with_zero_qty(client):
    """Заказ с нулевым количеством. Эндпоинт: POST /api/orders"""
    body = {"customer": CUSTOMER, "items": [{"book_id": 1, "qty": 0}]}
    response = client.post("/api/orders", json=body)
    assert response.status_code == 422

@pytest.mark.negative
def test_pay_already_paid_order(client):
    """Повторная оплата уже оплаченного заказа (запрещенный переход). Эндпоинт: POST /api/orders/{id}/pay"""
    order_resp = client.post("/api/orders", json={"customer": CUSTOMER, "items": [{"book_id": 1, "qty": 1}]})
    order_id = order_resp.json()["id"]
    client.post(f"/api/orders/{order_id}/pay") # Первый раз платим
    
    response = client.post(f"/api/orders/{order_id}/pay") # Второй раз
    assert response.status_code == 409

@pytest.mark.negative
def test_cancel_delivered_order(client):
    """Отмена уже доставленного заказа (запрещенный переход). Эндпоинт: POST /api/orders/{id}/cancel"""
    order_resp = client.post("/api/orders", json={"customer": CUSTOMER, "items": [{"book_id": 1, "qty": 1}]})
    order_id = order_resp.json()["id"]
    # Проводим заказ по всему жизненному циклу
    client.post(f"/api/orders/{order_id}/pay")
    client.post(f"/api/orders/{order_id}/ship")
    client.post(f"/api/orders/{order_id}/deliver")
    
    response = client.post(f"/api/orders/{order_id}/cancel")
    assert response.status_code == 409

@pytest.mark.negative
def test_create_order_exceeding_stock(client):
    """Заказ количества, превышающего остаток на складе. Эндпоинт: POST /api/orders"""
    # Сначала узнаем реальный остаток
    stock = client.get("/api/books/1").json()["stock"]
    body = {"customer": CUSTOMER, "items": [{"book_id": 1, "qty": stock + 1}]}
    
    response = client.post("/api/orders", json=body)
    assert response.status_code == 409 or response.status_code == 422
    
@pytest.mark.negative
@pytest.mark.xfail(strict=True, reason="Issue #4: Invalid book_id вызывает 500 вместо 404")
def test_create_order_with_invalid_book_id(client):
    body = {"customer": CUSTOMER, "items": [{"book_id": 99999, "qty": 1}]}
    response = client.post("/api/orders", json=body)
    assert response.status_code in [404, 422]
