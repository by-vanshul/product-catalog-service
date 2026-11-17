import uuid
from typing import List
from fastapi import APIRouter
from fastapi import HTTPException
from app.schemas.product import ProductCreate, ProductUpdate
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

products: List[dict] = []


@router.post("/products", status_code=201)
def create_product(product: ProductCreate):
    product_data = {
        "id": str(uuid.uuid4()),
        "created_at": datetime.utcnow().isoformat(),
        **product.model_dump()
    }
    products.append(product_data)
    logger.info(
        f"Product created successfully. Product ID: {product_data['id']}"
    )
    return product_data


@router.get("/products")
def get_products():

    logger.info(
        f"Retrieved all products. Count: {len(products)}"
    )

    return products


@router.get("/products/{product_id}")
def get_product(product_id: str):

    for product in products:
        if product["id"] == product_id:
            logger.info(
                f"Product retrieved. Product ID: {product_id}"
            )
            return product

    logger.warning(
        f"Product not found. Product ID: {product_id}"
    )

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

            logger.info(
                f"Product updated. Product ID: {product_id}"
            )

            return product

    logger.warning(
        f"Product not found. Product ID: {product_id}"
    )

    raise HTTPException(
        status_code=404,
        detail="Product not found"
    )


@router.delete("/products/{product_id}")
def delete_product(product_id: str):

    for index, product in enumerate(products):

        if product["id"] == product_id:

            deleted_product = products.pop(index)

            logger.info(
                f"Product deleted. Product ID: {product_id}"
            )

            return deleted_product

    logger.warning(
        f"Product not found. Product ID: {product_id}"
    )

    raise HTTPException(
        status_code=404,
        detail="Product not found"
    )