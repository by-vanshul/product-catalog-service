import uuid
from typing import List
from fastapi import APIRouter
from fastapi import HTTPException
from app.schemas.product import ProductCreate, ProductUpdate


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


@router.put("/products/{product_id}")
def update_product(product_id: str, updated_product: ProductUpdate):

    for product in products:

        if product["id"] == product_id:

            update_data = updated_product.model_dump(
                exclude_unset=True
            )

            product.update(update_data)

            return product

    raise HTTPException(
        status_code=404,
        detail="Product not found"
    )


@router.delete("/products/{product_id}")
def delete_product(product_id: str):

    for index, product in enumerate(products):

        if product["id"] == product_id:

            deleted_product = products.pop(index)

            return deleted_product

    raise HTTPException(
        status_code=404,
        detail="Product not found"
    )