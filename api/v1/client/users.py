from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from models.user import User
from schemas.user_schema import UserResponse
from api.dependencies import get_current_user
from services.storage_service import upload_to_supabase

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """
    Sadece giriş yapmış kullanıcıların kendi profil bilgilerini görmesini sağlar.
    """
    return current_user

@router.post("/upload-avatar")
def upload_avatar(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Kullanıcının profil fotoğrafını yükler ve veritabanını günceller.
    """
    # 1. Dosyayı Supabase 'avatars' bucket'ına yükle
    image_url = upload_to_supabase(file, bucket="avatars", folder="profiles")
    
    if not image_url:
        raise HTTPException(status_code=500, detail="Dosya yüklenirken bir hata oluştu.")
    
    # 2. Veritabanındaki URL'i güncelle
    current_user.profile_image_url = image_url
    db.commit()
    
    return {"status": "success", "image_url": image_url}