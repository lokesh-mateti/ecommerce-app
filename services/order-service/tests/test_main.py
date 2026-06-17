import respx
import httpx
from fastapi.testclient import TestClient
from app.main import app
from app.routes import PRODUCT_SERVICE_URL

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root():
    response = client.get("/")
    assert response.status_code == 200


@respx.mock
def test_create_order_success():
    # Mock product-service responding that the product exists
    respx.get(f"{PRODUCT_SERVICE_URL}/api/v1/products/prod-123").mock(
        return_value=httpx.Response(200, json={"id": "prod-123", "name": "Test"})
    )

    payload = {
        "customer_id": "cust-1",
        "items": [{"product_id": "prod-123", "quantity": 2, "unit_price": 10.0}],
    }
    response = client.post("/api/v1/orders/", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["total_amount"] == 20.0
    assert body["status"] == "pending"


@respx.mock
def test_create_order_product_not_found():
    respx.get(f"{PRODUCT_SERVICE_URL}/api/v1/products/prod-missing").mock(
        return_value=httpx.Response(404)
    )

    payload = {
        "customer_id": "cust-1",
        "items": [{"product_id": "prod-missing", "quantity": 1, "unit_price": 10.0}],
    }
    response = client.post("/api/v1/orders/", json=payload)
    assert response.status_code == 400


@respx.mock
def test_create_order_product_service_down():
    respx.get(f"{PRODUCT_SERVICE_URL}/api/v1/products/prod-1").mock(
        side_effect=httpx.ConnectError("connection failed")
    )

    payload = {
        "customer_id": "cust-1",
        "items": [{"product_id": "prod-1", "quantity": 1, "unit_price": 10.0}],
    }
    response = client.post("/api/v1/orders/", json=payload)
    assert response.status_code == 503


def test_get_nonexistent_order():
    response = client.get("/api/v1/orders/nonexistent-id")
    assert response.status_code == 404


@respx.mock
def test_update_order_status():
    respx.get(f"{PRODUCT_SERVICE_URL}/api/v1/products/prod-1").mock(
        return_value=httpx.Response(200, json={"id": "prod-1"})
    )
    create_payload = {
        "customer_id": "cust-1",
        "items": [{"product_id": "prod-1", "quantity": 1, "unit_price": 5.0}],
    }
    create_response = client.post("/api/v1/orders/", json=create_payload)
    order_id = create_response.json()["id"]

    update_response = client.patch(
        f"/api/v1/orders/{order_id}/status", json={"status": "confirmed"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "confirmed"


def test_list_orders():
    response = client.get("/api/v1/orders/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
