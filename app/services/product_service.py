import logging

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


logger = logging.getLogger(__name__)


def create_product(db: Session, product: ProductCreate) -> Product:
    try:
        db_product = Product(
            name=product.name,
            category=product.category,
            price=product.price,
            quantity=product.quantity,
        )
        db.add(db_product)
        db.commit()
        db.refresh(db_product)

        logger.info(
            "Product created successfully. Product ID: %s",
            db_product.id,
        )
        return db_product

    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Failed to create product: %s", exc)
        
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        ) from exc


def get_products(
    db: Session,
    name: str | None = None,
    category: str | None = None,
) -> list[Product]:
    try:
        query = db.query(Product)
        if name is not None:
            query = query.filter(Product.name.ilike(f"%{name}%"))
        if category is not None:
            query = query.filter(Product.category.ilike(f"%{category}%"))
        products = query.all()
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Failed to retrieve products: %s", exc)
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        ) from exc

    logger.info("Retrieved all products. Count: %s", len(products))
    return products


def get_product_by_id(db: Session, product_id: str) -> Product | None:
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Failed to retrieve product %s: %s", product_id, exc)
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        ) from exc

    if product is None:
        logger.warning("Product not found. Product ID: %s", product_id)
        return None

    logger.info("Product retrieved. Product ID: %s", product_id)
    return product


def update_product(db: Session, product_id: str, updated_product: ProductUpdate,) -> Product | None:
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if product is None:
            logger.warning("Product not found. Product ID: %s", product_id)
            return None

        for field, value in updated_product.model_dump(exclude_unset=True).items():
            setattr(product, field, value)

        db.commit()
        db.refresh(product)
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Failed to update product %s: %s", product_id, exc)
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        ) from exc

    logger.info("Product updated. Product ID: %s", product_id)
    return product


def delete_product(db: Session, product_id: str) -> Product | None:
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if product is None:
            logger.warning("Product not found. Product ID: %s", product_id)
            return None

        db.delete(product)
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error("Failed to delete product %s: %s", product_id, exc)
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        ) from exc

    logger.info("Product deleted. Product ID: %s", product_id)
    return product
