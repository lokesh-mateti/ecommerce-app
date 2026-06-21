from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TokenRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    exp: int


# ── Product schemas ──────────────────────────────────────────────
class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: Optional[str] = None
    stock_quantity: int = 0


class Product(ProductCreate):
    id: str


# ── Order schemas ────────────────────────────────────────────────
class OrderItem(BaseModel):
    product_id: str
    quantity: int
    unit_price: float


class OrderCreate(BaseModel):
    customer_id: str
    items: List[OrderItem]


class Order(BaseModel):
    id: str
    customer_id: str
    items: List[OrderItem]
    status: str
    total_amount: float
    created_at: datetime
    updated_at: datetime
