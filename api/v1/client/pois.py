import json
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from core.database import get_db
from core.config import settings
from core.redis_client import redis_db
from models.poi import POI
from services.poi_service import get_nearby_pois

router = APIRouter()


@router.get("/")
def get_all_pois(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Tüm mekanları (sayfalı) listeler. Redis ile önbelleklenir.
    Cache anahtarı sayfa bazlıdır; admin yeni POI eklediğinde 'client_pois:*' temizlenir.
    """
    cache_key = f"client_pois:limit={limit}:offset={offset}"

    if redis_db:
        cached = redis_db.get(cache_key)
        if cached:
            return json.loads(cached)

    pois = db.query(POI).order_by(POI.id).offset(offset).limit(limit).all()
    pois_data = [
        {
            "id": str(poi.id),
            "category": poi.category,
            "latitude": poi.latitude,
            "longitude": poi.longitude,
        }
        for poi in pois
    ]

    if redis_db:
        redis_db.setex(cache_key, 3600, json.dumps(pois_data))

    return pois_data


@router.get("/nearby")
def get_nearby_locations(
    lat: float,
    lng: float,
    radius_km: int = 5,
    lang: str = settings.DEFAULT_LANGUAGE,
    db: Session = Depends(get_db),
):
    """Kullanıcının enlem/boylamına göre yakındaki mekanları (en yakından uzağa) döndürür."""
    return get_nearby_pois(db=db, lat=lat, lng=lng, radius_km=radius_km, lang=lang)