from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel
from app.db.base import get_db
from app.models.product import Product
from app.models.batch_progress import BatchProgress
from app.schemas.product import ProductCreate, ProductResponse, BatchRequest
from app.services.product import ProductService
from sqlalchemy import select, func, text
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/amazon", tags=["amazon"])

@router.post("/process-batch")
async def process_batch(
    batch_request: BatchRequest,
    db: AsyncSession = Depends(get_db)
):
    """Toplu ürün işleme endpoint'i"""
    try:
        product_service = ProductService(db)
        products = batch_request.products
        
        logger.info(f"Toplu işleme başlatılıyor: {len(products)} ürün")
        
        # Boş string'leri None'a çevir
        for product in products:
            for field, value in product.dict().items():
                if value == "":
                    setattr(product, field, None)
        
        # Ürünleri toplu olarak işle
        processed_products = await product_service.create_products_batch(products)
        
        logger.info(f"Toplu işleme tamamlandı: {len(processed_products)} ürün işlendi")
        return {"status": "success", "processed_count": len(processed_products)}
        
    except Exception as e:
        logger.error(f"Toplu işleme hatası: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/batch-status")
async def check_batch_status(
    total_products: int,
    batch_size: int,
    db: AsyncSession = Depends(get_db)
):
    """Batch işlem durumunu kontrol et"""
    try:
        logger.debug(f"Batch durumu kontrol ediliyor: {total_products} ürün, {batch_size} batch boyutu")
        
        # En son batch progress kaydını al
        stmt = select(BatchProgress).order_by(BatchProgress.created_at.desc()).limit(1)
        result = await db.execute(stmt)
        last_progress = result.scalar_one_or_none()
        
        if not last_progress:
            # Yeni batch progress kaydı oluştur
            total_batches = (total_products + batch_size - 1) // batch_size
            new_progress = BatchProgress(
                total_products=total_products,
                batch_size=batch_size,
                last_completed_batch=0,
                total_batches=total_batches
            )
            db.add(new_progress)
            await db.commit()
            await db.refresh(new_progress)
            
            return {
                "status": "new",
                "total_products": total_products,
                "batch_size": batch_size,
                "total_batches": total_batches,
                "last_completed_batch": 0
            }
        
        # Mevcut batch progress'i kontrol et
        if (last_progress.total_products != total_products or 
            last_progress.batch_size != batch_size):
            # Farklı batch parametreleri, yeni kayıt oluştur
            total_batches = (total_products + batch_size - 1) // batch_size
            new_progress = BatchProgress(
                total_products=total_products,
                batch_size=batch_size,
                last_completed_batch=0,
                total_batches=total_batches
            )
            db.add(new_progress)
            await db.commit()
            await db.refresh(new_progress)
            
            return {
                "status": "new",
                "total_products": total_products,
                "batch_size": batch_size,
                "total_batches": total_batches,
                "last_completed_batch": 0
            }
        
        # Mevcut batch progress'i güncelle
        last_progress.last_completed_batch += 1
        await db.commit()
        await db.refresh(last_progress)
        
        return {
            "status": "continue",
            "total_products": last_progress.total_products,
            "batch_size": last_progress.batch_size,
            "total_batches": last_progress.total_batches,
            "last_completed_batch": last_progress.last_completed_batch
        }
        
    except Exception as e:
        logger.error(f"Batch durumu kontrol hatası: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products", response_model=List[ProductResponse])
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