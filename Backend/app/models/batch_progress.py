from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class BatchProgress(Base):
    __tablename__ = "batch_progress"

    id = Column(Integer, primary_key=True, index=True)
    total_products = Column(Integer)
    batch_size = Column(Integer)
    last_completed_batch = Column(Integer)
    total_batches = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 