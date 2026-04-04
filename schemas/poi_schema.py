from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

# 1. Çeviri verileri için alt şema (Polylang mantığı)
class POITranslationCreate(BaseModel):
    language_code: str # 'tr', 'en'
    name: str
    address: Optional[str] = None
    description: Optional[str] = None

# 2. Ana mekan oluşturma şeması (İçinde çevirileri de liste olarak barındırır)
class POICreate(BaseModel):
    latitude: float
    longitude: float
    category: str
    phone_number: Optional[str] = None
    website_url: Optional[str] = None
    entrance_fee: Optional[float] = None
    avg_time_spent: int
    translations: List[POITranslationCreate] # Çevirileri buraya dizi olarak ekleyeceğiz

# 3. Başarılı kayıt sonrası dönecek cevap şeması
class POIResponse(BaseModel):
    id: UUID
    message: str