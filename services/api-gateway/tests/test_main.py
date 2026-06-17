import respx
import httpx
from fastapi.testclient import TestClient
from app.main import app
from app.routes import PRODUCT_SERVICE_URL, ORDER_SERVICE_URL

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_login_success():
    response = client.post(
        "/auth/login", json={"username": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_invalid_credentials():
    response = client.post(
        "/auth/login", json={"username": "admin", "password": "wrongpass"}
    )
    assert response.status_code == 401


def test_proxy_route_without_token_rejected():
    response = client.get("/api/v1/products/")
    assert response.status_code in (401, 422)  # missing Authorization header


def _get_token():
    response = client.post(
        "/auth/login", json={"username": "admin", "password": "admin123"}
    )
    return response.json()["access_token"]


def test_proxy_route_with_invalid_token_rejected():
    response = client.get(
        "/api/v1/products/", headers={"Authorization": "Bearer invalid-token"}
    )
    assert response.status_code == 401


@respx.mock
def test_proxy_route_to_product_service():
    token = _get_token()
    respx.get(f"{PRODUCT_SERVICE_URL}/api/v1/products/").mock(
        return_value=httpx.Response(200, json=[])
    )

    response = client.get(
        "/api/v1/products/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


@respx.mock
def test_proxy_route_to_order_service():
    token = _get_token()
    respx.get(f"{ORDER_SERVICE_URL}/api/v1/orders/").mock(
        return_value=httpx.Response(200, json=[])
    )

    response = client.get(
        "/api/v1/orders/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


@respx.mock
def test_proxy_route_upstream_down():
    token = _get_token()
    respx.get(f"{PRODUCT_SERVICE_URL}/api/v1/products/").mock(
        side_effect=httpx.ConnectError("connection failed")
    )

    response = client.get(
        "/api/v1/products/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 503
