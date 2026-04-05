from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from models.poi import POI, POITranslation, POIImage
from models.user import User
from schemas.poi_schema import POICreate, POIResponse
from api.dependencies import get_admin_user
from services.storage_service import upload_to_supabase

router = APIRouter()

@router.post("/", response_model=POIResponse, status_code=status.HTTP_201_CREATED)
def create_poi(
    poi_data: POICreate, 
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user) 
):
    """
    (SADECE ADMİNLER İÇİN) Sisteme yeni bir mekan (POI) ve dillerini ekler.
    """
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

    for translation in poi_data.translations:
        new_translation = POITranslation(
            poi_id=new_poi.id,
            language_code=translation.language_code,
            name=translation.name,
            address=translation.address,
            description=translation.description
        )
        db.add(new_translation)
    
    db.commit()
    return {"id": new_poi.id, "message": "Mekan ve çevirileri başarıyla eklendi."}

# SWAGGER'I KANDIRAN KESİN ÇÖZÜM: Tıpkı Avatar gibi tek dosya alıyoruz!
@router.post("/{poi_id}/images", status_code=status.HTTP_201_CREATED)
def upload_poi_image(
    poi_id: str,
    file: UploadFile = File(...), # DİKKAT: Liste yok, tek dosya var!
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """
    (SADECE ADMİNLER İÇİN) Belirli bir mekana tek bir fotoğraf yükler.
    Çoklu yükleme için mobil uygulama bu endpoint'i döngü içinde çağırır.
    """
    # 1. Mekan var mı?
    poi = db.query(POI).filter(POI.id == poi_id).first()
    if not poi:
        raise HTTPException(status_code=404, detail="Mekan bulunamadı.")

    # 2. Dosyayı Supabase'e fırlat
    image_url = upload_to_supabase(file, bucket="poi_images", folder=str(poi_id))
    
    if not image_url:
        raise HTTPException(status_code=500, detail="Dosya yüklenemedi.")
        
    # 3. URL'i veritabanına kaydet
    new_image = POIImage(poi_id=poi.id, image_url=image_url)
    db.add(new_image)
    db.commit()
    
    return {
        "status": "success", 
        "message": "Fotoğraf başarıyla eklendi.",
        "image_url": image_url
    }