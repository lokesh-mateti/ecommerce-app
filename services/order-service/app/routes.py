import os
import httpx
from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import List

from app.models import Order, OrderCreate, OrderStatusUpdate

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])

# In-memory store for demo purposes.
_orders_db: dict[str, Order] = {}

# In EKS this resolves via Kubernetes Service DNS, e.g. "product-service.default.svc.cluster.local"
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8001")


async def _validate_product_exists(product_id: str) -> bool:
    """Calls product-service to confirm a product exists before placing an order."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(
                f"{PRODUCT_SERVICE_URL}/api/v1/products/{product_id}"
            )
            return response.status_code == 200
    except httpx.RequestError:
        # If product-service is unreachable, fail safe rather than silently allowing bad orders.
        raise HTTPException(
            status_code=503, detail="Product service unavailable, cannot validate order"
        )


@router.get("/", response_model=List[Order])
def list_orders():
    return list(_orders_db.values())


@router.get("/{order_id}", response_model=Order)
def get_order(order_id: str):
    order = _orders_db.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.post("/", response_model=Order, status_code=201)
async def create_order(payload: OrderCreate):
    for item in payload.items:
        exists = await _validate_product_exists(item.product_id)
        if not exists:
            raise HTTPException(
                status_code=400,
                detail=f"Product {item.product_id} does not exist",
            )

    total = sum(item.quantity * item.unit_price for item in payload.items)
    order = Order(
        customer_id=payload.customer_id,
        items=payload.items,
        total_amount=round(total, 2),
    )
    _orders_db[order.id] = order
    return order


@router.patch("/{order_id}/status", response_model=Order)
def update_order_status(order_id: str, payload: OrderStatusUpdate):
    order = _orders_db.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = payload.status
    order.updated_at = datetime.utcnow()
    _orders_db[order_id] = order
    return order


@router.delete("/{order_id}", status_code=204)
def cancel_order(order_id: str):
    order = _orders_db.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = "cancelled"
    _orders_db[order_id] = order
