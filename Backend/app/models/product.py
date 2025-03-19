from sqlalchemy import Column, Integer, String, Text, DateTime, Index, UniqueConstraint, Float
from sqlalchemy.sql import func
from app.db.base import Base

class Product(Base):
    __tablename__ = "amazon_products"

    id = Column(Integer, primary_key=True)
    asin = Column(String(255), nullable=True, unique=True)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    category = Column(String(255), nullable=True)
    ean = Column(String(255), nullable=True)
    rank = Column(Integer, nullable=True)
    sp1_stock = Column(Integer, nullable=True)
    sp2_stock = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Performans için indeksler
    __table_args__ = (
        Index('idx_amazon_products_asin', 'asin'),
    )

    def __repr__(self):
        return f"<Product {self.asin}>" 