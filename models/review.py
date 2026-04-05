import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from core.database import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Kim Yaptı? Nereye Yaptı?
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    poi_id = Column(UUID(as_uuid=True), ForeignKey("pois.id", ondelete="CASCADE"), nullable=False)
    
    # 1 ile 5 arasında yıldız verebilir
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True) # Yorum yazmak zorunda değil, sadece yıldız da verebilir
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # GÜVENLİK KURALLARI VERİTABANI SEVİYESİNDE:
    __table_args__ = (
        # 1. Puan 1 ile 5 arasında olmak zorundadır
        CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
        # 2. Bir kullanıcı bir mekana sadece 1 kez yorum yapabilir
        UniqueConstraint('user_id', 'poi_id', name='uq_user_poi_review'),
    )