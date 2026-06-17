from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime
import uuid


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderItem(BaseModel):
    product_id: str
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)


class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    items: List[OrderItem]
    status: OrderStatus = OrderStatus.PENDING
    total_amount: float = Field(default=0.0, ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": "cust-1234",
                "items": [
                    {"product_id": "prod-5678", "quantity": 2, "unit_price": 19.99}
                ],
            }
        }


class OrderCreate(BaseModel):
    customer_id: str
    items: List[OrderItem]


class OrderStatusUpdate(BaseModel):
    status: OrderStatus
