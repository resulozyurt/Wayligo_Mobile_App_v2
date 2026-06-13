from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID


# Kullanıcının yeni bir tatil oluştururken göndereceği veriler
class TripCreate(BaseModel):
    start_location: str
    destination_location: str
    start_date: datetime
    end_date: datetime
    transportation_type: str
    companion_type: str
    trip_concept: Optional[List[str]] = None  # Örn: ["gastronomy", "historical"]
    allow_route_deviations: Optional[bool] = True
    break_preference: Optional[int] = 3
    needs_hotel_rec: Optional[bool] = False


# Frontend'e dönecek güvenli format
class TripResponse(TripCreate):
    id: UUID
    user_id: UUID
    route_polyline: Optional[str] = None
    ai_itinerary: Optional[Any] = None  # JSON verisi

    class Config:
        from_attributes = True


# --- Rota Durakları (POI) Şemaları ---
class TripItemBase(BaseModel):
    poi_id: UUID
    order_index: int


class TripItemResponse(BaseModel):
    id: UUID
    trip_id: UUID
    poi_id: UUID
    order_index: int

    # ZENGİNLEŞTİRİLDİ: POI bilgisi de geliyor; mobil her durak için ayrı istek atmaz (N+1 yok).
    poi_name: Optional[str] = None
    poi_category: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    class Config:
        from_attributes = True


# Rota detayı + içindeki duraklar
class TripDetailResponse(TripResponse):
    items: List[TripItemResponse] = []