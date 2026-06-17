from pydantic import BaseModel, Field
from typing import Optional
import uuid


class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    price: float = Field(gt=0, description="Price must be greater than zero")
    category: str
    stock_quantity: int = Field(ge=0, default=0)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Wireless Mouse",
                "description": "Ergonomic wireless mouse with USB receiver",
                "price": 19.99,
                "category": "Electronics",
                "stock_quantity": 150,
            }
        }


class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = Field(gt=0)
    category: str
    stock_quantity: int = Field(ge=0, default=0)


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    category: Optional[str] = None
    stock_quantity: Optional[int] = Field(default=None, ge=0)
