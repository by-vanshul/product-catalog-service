from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    price: float = Field(..., ge=0)
    quantity: int = Field(..., ge=0)

class ProductUpdate(BaseModel):
    name: str | None = Field(None, min_length=1)
    category: str | None = Field(None, min_length=1)
    price: float | None = Field(None, ge=0)
    quantity: int | None = Field(None, ge=0)