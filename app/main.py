from fastapi import FastAPI
from app.api.products import router as product_router
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI(title="Product Catalog Service")

app.include_router(product_router)


@app.get("/")
def root():
    return {"message": "Product Catalog Service"}


@app.get("/health")
def health():
    return {"status": "UP"}