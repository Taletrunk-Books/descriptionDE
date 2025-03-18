from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from app.schemas.product import ProductCreate, ProductResponse
from app.services.product import ProductService
from app.core.config import settings

router = APIRouter()

@router.post("/bulk", response_model=List[ProductResponse])
async def create_products_bulk(
    products: List[ProductCreate],
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Toplu ürün ekleme endpoint'i.
    Rate limiting ve performans optimizasyonu için batch işleme yapar.
    """
    # Batch işleme
    batch_size = settings.BATCH_SIZE
    results = []
    
    for i in range(0, len(products), batch_size):
        batch = products[i:i + batch_size]
        product_service = ProductService(db)
        batch_results = await product_service.create_bulk(batch)
        results.extend(batch_results)
    
    return results

@router.get("/{asin}", response_model=ProductResponse)
async def get_product(
    asin: str,
    db: AsyncSession = Depends(get_db)
):
    """
    ASIN'e göre ürün getirme endpoint'i
    """
    product_service = ProductService(db)
    product = await product_service.get_by_asin(asin)
    
    if not product:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")
    
    return product

@router.get("/ean/{ean}", response_model=ProductResponse)
async def get_product_by_ean(
    ean: str,
    db: AsyncSession = Depends(get_db)
):
    """
    EAN'e göre ürün getirme endpoint'i
    """
    product_service = ProductService(db)
    product = await product_service.get_by_ean(ean)
    
    if not product:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")
    
    return product 