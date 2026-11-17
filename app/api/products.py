from fastapi import APIRouter
from app.schemas.product import ProductCreate
from typing import List


router = APIRouter()

products: List[ProductCreate] = []


@router.post("/products")
def create_product(product: ProductCreate):
    products.append(product)
    return product