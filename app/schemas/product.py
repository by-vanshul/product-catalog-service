from datetime import datetime

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


class ProductResponse(BaseModel):
    id: str
    name: str
    category: str
    price: float
    quantity: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }