from fastapi import FastAPI

from app.api.products import router as product_router

app = FastAPI(title="Product Catalog Service")

app.include_router(product_router)


@app.get("/")
def root():
    return {"message": "Product Catalog Service"}


@app.get("/health")
def health():
    return {"status": "UP"}