from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from models.favorite import Favorite
from models.poi import POI
from models.user import User
from api.dependencies import get_current_user
from uuid import UUID

router = APIRouter()

@router.post("/{poi_id}/toggle")
def toggle_favorite(poi_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Mekan zaten favorilerdeyse çıkarır (Unlike), değilse ekler (Like).
    Mobil uygulama için en ideal ve hızlı 'Aç/Kapat' mantığıdır.
    """
    # 1. Mekan gerçekten var mı?
    poi = db.query(POI).filter(POI.id == poi_id).first()
    if not poi:
        raise HTTPException(status_code=404, detail="Mekan bulunamadı.")

    # 2. Bu kullanıcı bu mekanı daha önce favorilemiş mi?
    existing_fav = db.query(Favorite).filter(Favorite.user_id == current_user.id, Favorite.poi_id == poi_id).first()
    
    if existing_fav:
        # Varsa favorilerden çıkar
        db.delete(existing_fav)
        db.commit()
        return {"status": "success", "message": "Mekan favorilerden çıkarıldı.", "is_favorite": False}
    else:
        # Yoksa favorilere ekle
        new_fav = Favorite(user_id=current_user.id, poi_id=poi_id)
        db.add(new_fav)
        db.commit()
        return {"status": "success", "message": "Mekan favorilere eklendi.", "is_favorite": True}

@router.get("/")
def get_my_favorites(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Kullanıcının favoriye eklediği mekanların listesini getirir.
    """
    # Veritabanında JOIN işlemi: Favoriler tablosuyla POI tablosunu birleştirip getir
    favorites = db.query(Favorite, POI).join(POI, Favorite.poi_id == POI.id).filter(Favorite.user_id == current_user.id).all()
    
    result = []
    for fav, poi in favorites:
        result.append({
            "favorite_id": str(fav.id),
            "poi_id": str(poi.id),
            "category": poi.category,
            "latitude": poi.latitude,
            "longitude": poi.longitude,
            "added_at": fav.created_at
        })
        
    return result