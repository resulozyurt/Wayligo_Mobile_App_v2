from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from models.review import Review
from models.poi import POI
from models.user import User
from api.dependencies import get_current_user
from pydantic import BaseModel
from uuid import UUID

router = APIRouter()

# Yorum Gönderme Şeması (Pydantic)
class ReviewCreate(BaseModel):
    rating: int
    comment: str | None = None

@router.post("/{poi_id}")
def add_review(poi_id: UUID, review_data: ReviewCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Mekana 1-5 arası puan ve yorum ekler."""
    if not (1 <= review_data.rating <= 5):
        raise HTTPException(status_code=400, detail="Puan 1 ile 5 arasında olmalıdır.")

    # Mekan var mı?
    poi = db.query(POI).filter(POI.id == poi_id).first()
    if not poi:
        raise HTTPException(status_code=404, detail="Mekan bulunamadı.")
        
    # Daha önce yorum yapmış mı?
    existing = db.query(Review).filter(Review.user_id == current_user.id, Review.poi_id == poi_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bu mekana daha önce yorum yaptınız.")

    new_review = Review(
        user_id=current_user.id,
        poi_id=poi_id,
        rating=review_data.rating,
        comment=review_data.comment
    )
    db.add(new_review)
    db.commit()
    
    return {"status": "success", "message": "Yorumunuz başarıyla eklendi."}

@router.get("/{poi_id}")
def get_poi_reviews(poi_id: UUID, db: Session = Depends(get_db)):
    """Bir mekanın tüm yorumlarını ve puanlarını listeler (Giriş yapmaya gerek yok)."""
    reviews = db.query(Review).filter(Review.poi_id == poi_id).all()
    return reviews