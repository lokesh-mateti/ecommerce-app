from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root():
    response = client.get("/")
    assert response.status_code == 200


def test_create_and_get_product():
    payload = {
        "name": "Test Product",
        "description": "A product for testing",
        "price": 9.99,
        "category": "Test",
        "stock_quantity": 10,
    }
    create_response = client.post("/api/v1/products/", json=payload)
    assert create_response.status_code == 201
    product_id = create_response.json()["id"]

    get_response = client.get(f"/api/v1/products/{product_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Test Product"


def test_get_nonexistent_product():
    response = client.get("/api/v1/products/nonexistent-id")
    assert response.status_code == 404


def test_create_product_invalid_price():
    payload = {
        "name": "Bad Product",
        "price": -5.0,
        "category": "Test",
    }
    response = client.post("/api/v1/products/", json=payload)
    assert response.status_code == 422


def test_list_products():
    response = client.get("/api/v1/products/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_delete_product():
    payload = {"name": "To Delete", "price": 5.0, "category": "Test"}
    create_response = client.post("/api/v1/products/", json=payload)
    product_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/products/{product_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/products/{product_id}")
    assert get_response.status_code == 404
