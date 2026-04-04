import uuid
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from core.database import Base

class Trip(Base):
    __tablename__ = "trips"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # YABANCI ANAHTAR (Foreign Key): Bu tatil hangi kullanıcıya ait?
    # ondelete="CASCADE": Kullanıcı silinirse, bu tatil planını da veritabanından tamamen sil.
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    start_location = Column(String, nullable=False)
    destination_location = Column(String, nullable=False)
    
    # Date yerine DateTime kullanıyoruz çünkü saat 09:00'da yola çıkılacak bilgisi kritik
    start_date = Column(DateTime, nullable=False) 
    end_date = Column(DateTime, nullable=False)
    
    transportation_type = Column(String, nullable=False)
    companion_type = Column(String, nullable=False)
    trip_concept = Column(JSONB, nullable=True)
    allow_route_deviations = Column(Boolean, default=True)
    break_preference = Column(Integer, default=3)
    needs_hotel_rec = Column(Boolean, default=False)

    # ... Üst kısımlar aynı kalacak ...
    allow_route_deviations = Column(Boolean, default=True)
    break_preference = Column(Integer, default=3)
    needs_hotel_rec = Column(Boolean, default=False)
    
    # --- YENİ EKLENEN HAFIZA ALANLARI ---
    # Haritadaki mavi çizgiyi (Polyline) kalıcı olarak saklıyoruz
    route_polyline = Column(String, nullable=True) 
    
    # Yapay zekanın ürettiği o detaylı JSON planını saklıyoruz
    ai_itinerary = Column(JSONB, nullable=True)