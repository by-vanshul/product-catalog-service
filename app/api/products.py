from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.services import product_service


router = APIRouter()

# The API layer handles HTTP concerns and delegates product operations to the service.


@router.post("/products", status_code=201, response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db),):
    return product_service.create_product(db, product)


@router.get("/products", response_model=list[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    return product_service.get_products(db)


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: str, db: Session = Depends(get_db)):
    product = product_service.get_product_by_id(db, product_id)
    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )
    return product


@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: str, updated_product: ProductUpdate, db: Session = Depends(get_db),):
    product = product_service.update_product(db, product_id, updated_product)
    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )
    return product


@router.delete("/products/{product_id}", response_model=ProductResponse)
def delete_product(product_id: str, db: Session = Depends(get_db)):
    product = product_service.delete_product(db, product_id)
    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )
    return product
