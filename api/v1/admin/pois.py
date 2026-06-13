from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from core.database import get_db
from core.redis_client import redis_db
from models.poi import POI, POITranslation, POIImage
from models.user import User
from schemas.poi_schema import POICreate, POIResponse
from api.dependencies import get_admin_user
from services.storage_service import upload_to_supabase

router = APIRouter()


def _invalidate_poi_cache() -> None:
    """
    Yeni mekan eklenince/güncellenince Redis'teki sayfalı POI listelerini temizler.
    Aksi halde mobil uygulama yeni mekanı 1 saate kadar göremezdi.
    """
    if redis_db:
        for key in redis_db.scan_iter("client_pois:*"):
            redis_db.delete(key)


@router.post("/", response_model=POIResponse, status_code=status.HTTP_201_CREATED)
def create_poi(
    poi_data: POICreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """(SADECE ADMİNLER) Yeni bir mekan (POI) ve çevirilerini ekler."""
    new_poi = POI(
        latitude=poi_data.latitude,
        longitude=poi_data.longitude,
        category=poi_data.category,
        phone_number=poi_data.phone_number,
        website_url=poi_data.website_url,
        entrance_fee=poi_data.entrance_fee,
        avg_time_spent=poi_data.avg_time_spent,
        # KRİTİK: geom'u DB trigger'ına bağlı bırakmıyoruz, burada dolduruyoruz.
        # Aksi halde geom NULL kalır ve ST_DWithin (nearby/route) bu mekanı bulamaz.
        geom=func.ST_SetSRID(
            func.ST_MakePoint(poi_data.longitude, poi_data.latitude), 4326
        ),
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
            description=translation.description,
        )
        db.add(new_translation)

    db.commit()

    # Yeni mekan eklendi -> önbellek bayatladı, temizle.
    _invalidate_poi_cache()

    return {"id": new_poi.id, "message": "Mekan ve çevirileri başarıyla eklendi."}


@router.post("/{poi_id}/images", status_code=status.HTTP_201_CREATED)
def upload_poi_image(
    poi_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """(SADECE ADMİNLER) Belirli bir mekana tek bir fotoğraf yükler."""
    poi = db.query(POI).filter(POI.id == poi_id).first()
    if not poi:
        raise HTTPException(status_code=404, detail="Mekan bulunamadı.")

    image_url = upload_to_supabase(file, bucket="poi_images", folder=str(poi_id))
    if not image_url:
        raise HTTPException(status_code=500, detail="Dosya yüklenemedi.")

    new_image = POIImage(poi_id=poi.id, image_url=image_url)
    db.add(new_image)
    db.commit()

    return {
        "status": "success",
        "message": "Fotoğraf başarıyla eklendi.",
        "image_url": image_url,
    }