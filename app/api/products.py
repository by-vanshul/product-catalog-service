import uuid
from typing import List
from fastapi import APIRouter
from fastapi import HTTPException
from app.schemas.product import ProductCreate


router = APIRouter()

products: List[dict] = []


@router.post("/products")
def create_product(product: ProductCreate):
    product_data = {
        "id": str(uuid.uuid4()),
        **product.model_dump()
    }
    products.append(product_data)
    return product_data


@router.get("/products")
def get_products():
    return products


@router.get("/products/{product_id}")
def get_product(product_id: str):

    for product in products:
        if product["id"] == product_id:
            return product

    raise HTTPException(
        status_code=404,
        detail="Product not found"
    )