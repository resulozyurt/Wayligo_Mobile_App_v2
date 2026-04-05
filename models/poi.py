import uuid
from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry # YENİ EKLENDİ: Coğrafi hesaplamalar için
from core.database import Base

# DİLDEN BAĞIMSIZ ANA TABLO (Koordinatlar, Fiyatlar vb.)
class POI(Base):
    __tablename__ = "pois"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    latitude = Column(Float, nullable=False) 
    longitude = Column(Float, nullable=False)
    
    # YENİ EKLENDİ: Coğrafi nokta (PostGIS için). nullable=True yaptık çünkü veriyi trigger ile dolduracağız.
    geom = Column(Geometry(geometry_type='POINT', srid=4326), nullable=True) 
    
    category = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    website_url = Column(String, nullable=True)
    entrance_fee = Column(Float, nullable=True) 
    avg_time_spent = Column(Integer, nullable=False)

    # --- YENİ EKLENEN YORUM SÜTUNLARI ---
    average_rating = Column(Float, default=0.0) # Ortala puan (Örn: 4.5)
    review_count = Column(Integer, default=0) # Kaç kişi yorum yaptı? (Örn: 120)

# ÇEVİRİ TABLOSU (Polylang Mantığı)
class POITranslation(Base):
    __tablename__ = "poi_translations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # YABANCI ANAHTAR: Bu çeviri hangi mekana ait?
    poi_id = Column(UUID(as_uuid=True), ForeignKey("pois.id", ondelete="CASCADE"), nullable=False)
    
    language_code = Column(String, nullable=False) # 'tr', 'en', 'fr'
    name = Column(String, nullable=False)
    address = Column(String, nullable=True)
    description = Column(Text, nullable=True)

class POIImage(Base):
    __tablename__ = "poi_images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # YABANCI ANAHTAR: Bu fotoğraf hangi mekana ait? (Mekan silinirse fotoğrafları da veritabanından silinir: CASCADE)
    poi_id = Column(UUID(as_uuid=True), ForeignKey("pois.id", ondelete="CASCADE"), nullable=False)
    
    image_url = Column(String, nullable=False)