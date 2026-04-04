from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from core.database import get_db
from models.poi import POI, POITranslation
from models.user import User
from schemas.poi_schema import POICreate, POIResponse
from api.dependencies import get_admin_user

router = APIRouter()

# DİKKAT: Depends(get_admin_user) ile burayı sadece adminlere açıyoruz.
@router.post("/", response_model=POIResponse, status_code=status.HTTP_201_CREATED)
def create_poi(
    poi_data: POICreate, 
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user) 
):
    """
    (SADECE ADMİNLER İÇİN) Sisteme yeni bir mekan (POI) ve dillerini ekler.
    """
    # 1. Önce dilden bağımsız ana veriyi kaydediyoruz
    new_poi = POI(
        latitude=poi_data.latitude,
        longitude=poi_data.longitude,
        category=poi_data.category,
        phone_number=poi_data.phone_number,
        website_url=poi_data.website_url,
        entrance_fee=poi_data.entrance_fee,
        avg_time_spent=poi_data.avg_time_spent
    )
    db.add(new_poi)
    db.commit()
    db.refresh(new_poi)

    # 2. Şimdi gelen dilleri (translations) teker teker veritabanına, bu mekana bağlayarak ekliyoruz
    for translation in poi_data.translations:
        new_translation = POITranslation(
            poi_id=new_poi.id, # Üstte oluşan ID ile bağlıyoruz
            language_code=translation.language_code,
            name=translation.name,
            address=translation.address,
            description=translation.description
        )
        db.add(new_translation)
    
    db.commit() # Tüm çevirileri kaydet

    return {"id": new_poi.id, "message": "Mekan ve çevirileri başarıyla eklendi."}