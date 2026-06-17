from fastapi import APIRouter, HTTPException
from typing import List

from app.models import Product, ProductCreate, ProductUpdate

router = APIRouter(prefix="/api/v1/products", tags=["products"])

# In-memory store for demo purposes.
# In production this would be replaced by a real database (Postgres/DynamoDB).
_products_db: dict[str, Product] = {}


@router.get("/", response_model=List[Product])
def list_products():
    return list(_products_db.values())


@router.get("/{product_id}", response_model=Product)
def get_product(product_id: str):
    product = _products_db.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", response_model=Product, status_code=201)
def create_product(payload: ProductCreate):
    product = Product(**payload.model_dump())
    _products_db[product.id] = product
    return product


@router.put("/{product_id}", response_model=Product)
def update_product(product_id: str, payload: ProductUpdate):
    product = _products_db.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = payload.model_dump(exclude_unset=True)
    updated_product = product.model_copy(update=update_data)
    _products_db[product_id] = updated_product
    return updated_product


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: str):
    if product_id not in _products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    del _products_db[product_id]
