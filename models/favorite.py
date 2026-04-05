import uuid
from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from core.database import Base

class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Hangi kullanıcı? (Kullanıcı silinirse favorileri de silinir: CASCADE)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Hangi mekan? (Mekan silinirse favori kaydı da silinir: CASCADE)
    poi_id = Column(UUID(as_uuid=True), ForeignKey("pois.id", ondelete="CASCADE"), nullable=False)
    
    # Ne zaman favoriye eklendi? (Sıralama yapmak için)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # GÜVENLİK: Bir kullanıcı aynı mekanı iki kez favorileyemez (Hata fırlatır veya engeller)
    __table_args__ = (UniqueConstraint('user_id', 'poi_id', name='uq_user_poi_favorite'),)