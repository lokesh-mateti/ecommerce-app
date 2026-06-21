import os
import json
import httpx
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List

from app.models import (
    TokenRequest, TokenResponse,
    ProductCreate, Product,
    OrderCreate, Order
)
from app.auth import authenticate_user, create_access_token, verify_token

router = APIRouter()
security = HTTPBearer()

PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8001")
ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://localhost:8002")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validates Bearer token from Authorize button — no manual header needed."""
    return verify_token(credentials.credentials)


@router.post("/auth/login", response_model=TokenResponse, tags=["auth"])
def login(payload: TokenRequest):
    if not authenticate_user(payload.username, payload.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(subject=payload.username)
    return TokenResponse(access_token=token)


async def _proxy(base_url: str, path: str, request: Request, body=None) -> JSONResponse:
    url = f"{base_url}{path}"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            content = json.dumps(body).encode() if body is not None else await request.body()
            response = await client.request(
                method=request.method,
                url=url,
                content=content,
                params=request.query_params,
                headers={"content-type": "application/json"},
            )
        return JSONResponse(
            status_code=response.status_code,
            content=response.json() if response.content else None,
        )
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail=f"Upstream service unavailable: {base_url}")


# ── Product endpoints ─────────────────────────────────────────────
@router.get("/api/v1/products/", response_model=List[Product], tags=["products"])
async def list_products(request: Request, user: str = Depends(get_current_user)):
    """List all products"""
    return await _proxy(PRODUCT_SERVICE_URL, "/api/v1/products/", request)


@router.post("/api/v1/products/", response_model=Product, status_code=201, tags=["products"])
async def create_product(payload: ProductCreate, request: Request, user: str = Depends(get_current_user)):
    """Create a new product"""
    return await _proxy(PRODUCT_SERVICE_URL, "/api/v1/products/", request, payload.model_dump())


@router.get("/api/v1/products/{product_id}", response_model=Product, tags=["products"])
async def get_product(product_id: str, request: Request, user: str = Depends(get_current_user)):
    """Get a product by ID"""
    return await _proxy(PRODUCT_SERVICE_URL, f"/api/v1/products/{product_id}", request)


@router.put("/api/v1/products/{product_id}", response_model=Product, tags=["products"])
async def update_product(product_id: str, payload: ProductCreate, request: Request, user: str = Depends(get_current_user)):
    """Update a product"""
    return await _proxy(PRODUCT_SERVICE_URL, f"/api/v1/products/{product_id}", request, payload.model_dump())


@router.delete("/api/v1/products/{product_id}", tags=["products"])
async def delete_product(product_id: str, request: Request, user: str = Depends(get_current_user)):
    """Delete a product"""
    return await _proxy(PRODUCT_SERVICE_URL, f"/api/v1/products/{product_id}", request)


# ── Order endpoints ───────────────────────────────────────────────
@router.get("/api/v1/orders/", response_model=List[Order], tags=["orders"])
async def list_orders(request: Request, user: str = Depends(get_current_user)):
    """List all orders"""
    return await _proxy(ORDER_SERVICE_URL, "/api/v1/orders/", request)


@router.post("/api/v1/orders/", response_model=Order, status_code=201, tags=["orders"])
async def create_order(payload: OrderCreate, request: Request, user: str = Depends(get_current_user)):
    """Create a new order"""
    return await _proxy(ORDER_SERVICE_URL, "/api/v1/orders/", request, payload.model_dump())


@router.get("/api/v1/orders/{order_id}", response_model=Order, tags=["orders"])
async def get_order(order_id: str, request: Request, user: str = Depends(get_current_user)):
    """Get an order by ID"""
    return await _proxy(ORDER_SERVICE_URL, f"/api/v1/orders/{order_id}", request)


@router.patch("/api/v1/orders/{order_id}/status", tags=["orders"])
async def update_order_status(order_id: str, request: Request, user: str = Depends(get_current_user)):
    """Update order status"""
    return await _proxy(ORDER_SERVICE_URL, f"/api/v1/orders/{order_id}/status", request)
