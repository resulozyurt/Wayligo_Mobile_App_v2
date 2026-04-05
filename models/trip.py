import uuid
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship # YENİ EKLENDİ
from core.database import Base

class Trip(Base):
    __tablename__ = "trips"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    start_location = Column(String, nullable=False)
    destination_location = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False) 
    end_date = Column(DateTime, nullable=False)
    transportation_type = Column(String, nullable=False)
    companion_type = Column(String, nullable=False)
    trip_concept = Column(JSONB, nullable=True)
    allow_route_deviations = Column(Boolean, default=True)
    break_preference = Column(Integer, default=3)
    needs_hotel_rec = Column(Boolean, default=False)
    
    route_polyline = Column(String, nullable=True) 
    ai_itinerary = Column(JSONB, nullable=True)

    # YENİ EKLENDİ: Bu rotaya ait duraklar (Mekanlar) ile bağlantı kuruyoruz
    items = relationship("TripItem", back_populates="trip", cascade="all, delete-orphan")

# --- YENİ EKLENEN TABLO: Rota Durakları (Trip Items) ---
class TripItem(Base):
    __tablename__ = "trip_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Hangi Rotaya Ait?
    trip_id = Column(UUID(as_uuid=True), ForeignKey("trips.id", ondelete="CASCADE"), nullable=False)
    # Hangi Mekan (POI) Eklendi?
    poi_id = Column(UUID(as_uuid=True), ForeignKey("pois.id", ondelete="CASCADE"), nullable=False)
    
    # Rotadaki sırası (1. durak, 2. durak vs.)
    order_index = Column(Integer, nullable=False)
    
    # İlişki Bağlantısı
    trip = relationship("Trip", back_populates="items")