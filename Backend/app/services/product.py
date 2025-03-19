from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert, func
from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
import logging

logger = logging.getLogger(__name__)

class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_product(self, product: ProductCreate) -> Product:
        """Yeni ürün oluştur"""
        try:
            db_product = Product(
                asin=product.asin,
                title=product.title,
                description=product.description,
                category=product.category,
                ean=product.ean,
                rank=product.rank,
                sp1_stock=product.sp1_stock,
                sp2_stock=product.sp2_stock
            )
            self.db.add(db_product)
            await self.db.commit()
            await self.db.refresh(db_product)
            return db_product
        except Exception as e:
            logger.error(f"Ürün oluşturma hatası: {str(e)}")
            await self.db.rollback()
            raise

    async def create_products_batch(self, products: list[ProductCreate]) -> list[Product]:
        """
        Ürünleri toplu olarak kaydet veya güncelle
        
        Args:
            products: Kaydedilecek ürünlerin listesi
            
        Returns:
            Kaydedilen/güncellenen ürünlerin listesi
        """
        try:
            # Ürünleri dictionary listesine dönüştür
            product_dicts = []
            for product in products:
                try:
                    product_dict = product.model_dump()
                    # Boş string'leri None'a çevir
                    for key, value in product_dict.items():
                        if isinstance(value, str) and not value.strip():
                            product_dict[key] = None
                    product_dicts.append(product_dict)
                except Exception as e:
                    logger.error(f"Ürün dönüştürme hatası: {str(e)}")
                    continue
            
            if not product_dicts:
                logger.warning("İşlenecek geçerli ürün bulunamadı")
                return []
            
            # UPSERT işlemi için SQLAlchemy insert yerine PostgreSQL insert kullan
            stmt = pg_insert(Product).values(product_dicts)
            stmt = stmt.on_conflict_do_update(
                index_elements=['asin'],
                set_={
                    'description': stmt.excluded.description,
                    'category': stmt.excluded.category,
                    'title': stmt.excluded.title,
                    'ean': stmt.excluded.ean,
                    'rank': stmt.excluded.rank,
                    'sp1_stock': stmt.excluded.sp1_stock,
                    'sp2_stock': stmt.excluded.sp2_stock,
                    'updated_at': func.now()
                }
            )
            
            await self.db.execute(stmt)
            await self.db.commit()
            
            # Eklenen/güncellenen ürünleri getir
            result = await self.db.execute(
                select(Product).where(Product.asin.in_([p.asin for p in products]))
            )
            processed_products = result.scalars().all()
            
            logger.info(f"{len(processed_products)} ürün başarıyla işlendi")
            return processed_products
            
        except Exception as e:
            logger.error(f"Ürün kaydetme hatası: {str(e)}")
            await self.db.rollback()
            raise

    async def get_products(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """Tüm ürünleri listele"""
        try:
            result = await self.db.execute(
                select(Product)
                .offset(skip)
                .limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Ürün listeleme hatası: {str(e)}")
            raise

    async def get_product_by_asin(self, asin: str) -> Optional[Product]:
        """ASIN'e göre ürün getir"""
        try:
            result = await self.db.execute(
                select(Product).where(Product.asin == asin)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Ürün getirme hatası: {str(e)}")
            raise

    async def get_by_ean(self, ean: str) -> Optional[Product]:
        """EAN'e göre ürün getirme"""
        query = select(Product).where(Product.ean == ean)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update(self, asin: str, product: ProductUpdate) -> Optional[Product]:
        """
        Ürün güncelle
        """
        stmt = (
            update(Product)
            .where(Product.asin == asin)
            .values(**product.model_dump(exclude_unset=True))
        )
        await self.db.execute(stmt)
        await self.db.commit()
        return await self.get_product_by_asin(asin)

    async def delete(self, asin: str) -> bool:
        """Ürün silme"""
        stmt = select(Product).where(Product.asin == asin)
        result = await self.db.execute(stmt)
        product = result.scalar_one_or_none()
        
        if product:
            await self.db.delete(product)
            await self.db.commit()
            return True
        return False 