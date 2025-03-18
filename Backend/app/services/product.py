from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.sql import func
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_products_batch(self, products: List[ProductCreate]) -> List[Product]:
        try:
            async with AsyncSession(self.db.bind) as session:
                # PostgreSQL için özel insert ifadesi
                stmt = pg_insert(Product).values([
                    {
                        'asin': product.asin,
                        'description': product.description,
                        'category': product.category,
                        'ean': product.ean,
                        'rank': product.rank,
                        'sp1_stock': product.sp1_stock,
                        'sp2_stock': product.sp2_stock
                    }
                    for product in products
                ]).on_conflict_do_update(
                    constraint='amazon_products_asin_key',
                    set_={
                        'description': pg_insert(Product).excluded.description,
                        'category': pg_insert(Product).excluded.category,
                        'ean': pg_insert(Product).excluded.ean,
                        'rank': pg_insert(Product).excluded.rank,
                        'sp1_stock': pg_insert(Product).excluded.sp1_stock,
                        'sp2_stock': pg_insert(Product).excluded.sp2_stock,
                        'updated_at': func.now()
                    }
                )

                await session.execute(stmt)
                await session.commit()

                # Eklenen/güncellenen kayıtları al
                asins = [product.asin for product in products]
                result = await session.execute(
                    select(Product).where(Product.asin.in_(asins))
                )
                return result.scalars().all()

        except Exception as e:
            print(f"Toplu ürün ekleme/güncelleme hatası: {e}")
            raise

    async def get_products(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """
        Tüm ürünleri listele
        """
        query = select(Product).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_asin(self, asin: str) -> Optional[Product]:
        """
        ASIN'e göre ürün getir
        """
        query = select(Product).where(Product.asin == asin)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

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
        return await self.get_by_asin(asin)

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