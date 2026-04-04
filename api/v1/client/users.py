from fastapi import APIRouter, Depends
from models.user import User
from schemas.user_schema import UserResponse
from api.dependencies import get_current_user

router = APIRouter()

# DİKKAT: response_model=UserResponse ile şifreyi gizliyoruz.
# DİKKAT: Depends(get_current_user) ile kapıya güvenlik görevlimizi dikiyoruz.
@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """
    Sadece giriş yapmış kullanıcıların kendi profil bilgilerini görmesini sağlar.
    """
    return current_user