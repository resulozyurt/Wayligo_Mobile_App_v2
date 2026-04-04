from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from typing import Any

# Kullanıcının yeni bir tatil oluştururken göndereceği veriler
class TripCreate(BaseModel):
    start_location: str
    destination_location: str
    start_date: datetime # Örn: "2026-05-10T09:00:00"
    end_date: datetime
    transportation_type: str
    companion_type: str
    trip_concept: Optional[List[str]] = None # Örn: ["gastronomy", "historical"]
    allow_route_deviations: Optional[bool] = True
    break_preference: Optional[int] = 3
    needs_hotel_rec: Optional[bool] = False

# Veritabanından veriyi çekerken frontend'e göndereceğimiz güvenli format
class TripResponse(TripCreate):
    id: UUID
    user_id: UUID
    
    # YENİ EKLENENLER: Veritabanındaki yeni sütunları dışarıya açıyoruz
    route_polyline: Optional[str] = None
    ai_itinerary: Optional[Any] = None # JSON verisi olduğu için Any diyoruz

    class Config:
        from_attributes = True