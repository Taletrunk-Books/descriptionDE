from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class ProductBase(BaseModel):
    asin: str = Field(..., max_length=10)
    ean: str = Field(..., max_length=13)
    rank: Optional[int] = None
    sp1_stock: Optional[int] = None
    sp2_stock: Optional[int] = None
    category: Optional[str] = None
    description: Optional[str] = None
    title: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    asin: Optional[str] = None
    ean: Optional[str] = None

class ProductResponse(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class BatchRequest(BaseModel):
    products: List[ProductCreate] 