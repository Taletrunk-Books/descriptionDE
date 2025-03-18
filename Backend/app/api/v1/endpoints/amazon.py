from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pydantic import BaseModel
from app.db.base import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductResponse
from app.services.product import ProductService

router = APIRouter()

class BatchRequest(BaseModel):
    products: List[ProductCreate]

@router.post("/amazon/batch", response_model=List[ProductResponse])
async def create_products_batch(
    request: BatchRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Toplu ürün kaydı oluştur
    """
    try:
        service = ProductService(db)
        created_products = await service.create_products_batch(request.products)
        return created_products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/amazon/products", response_model=List[ProductResponse])
async def get_products(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Tüm ürünleri listele
    """
    try:
        service = ProductService(db)
        products = await service.get_products(skip=skip, limit=limit)
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 