import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from core.redis_client import redis_db
from models.poi import POI

router = APIRouter()

@router.get("/")
def get_all_pois(db: Session = Depends(get_db)):
    """
    Sistemdeki tüm mekanları (POI) listeler.
    Redis önbellekleme (Caching) mimarisi ile donatılmıştır.
    """
    cache_key = "all_client_pois"
    
    # 1. Önce Redis'in hafızasına (RAM) bakıyoruz
    if redis_db:
        cached_pois = redis_db.get(cache_key)
        if cached_pois:
            # Geliştirici olarak terminalde görebilmen için eklendi
            print("⚡ VERİ REDIS'TEN (RAM) GELDİ! (Milisaniye seviyesi)") 
            return json.loads(cached_pois)

    # 2. Eğer Redis'te yoksa (Cache Miss), mecburen PostgreSQL'e (Disk) iniyoruz
    print("🐌 VERİ POSTGRESQL'DEN (Disk) GELDİ.")
    pois = db.query(POI).all()
    
    # Veritabanından gelen nesneleri JSON formatına çevrilecek bir listeye dönüştürüyoruz
    pois_data = []
    for poi in pois:
        pois_data.append({
            "id": str(poi.id),
            "category": poi.category,
            "latitude": poi.latitude,
            "longitude": poi.longitude
            # Şimdilik ana verileri dönüyoruz, ileride çeviriler vb. de eklenebilir
        })
        
    # 3. Veriyi PostgreSQL'den aldık, bir kopyasını 1 saat (3600 saniye) boyunca Redis'e kaydediyoruz
    if redis_db:
        redis_db.setex(cache_key, 3600, json.dumps(pois_data))
        
    return pois_data