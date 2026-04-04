from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from core.database import get_db
from models.user import User


# Şemalarımızı ve Güvenlik fonksiyonlarımızı güncelledik
from schemas.user_schema import UserCreate, UserLogin, Token
from core.security import get_password_hash, verify_password, create_access_token

router = APIRouter()

# --- KAYIT OL (REGISTER) --- (Buraya dokunmadık, aynı kalıyor)
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter((User.email == user.email) | (User.username == user.username)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Bu e-posta adresi veya kullanıcı adı zaten sistemde kayıtlı.")

    hashed_pw = get_password_hash(user.password)
    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        username=user.username,
        password_hash=hashed_pw,
        residence_city=user.residence_city,
        has_vehicle=user.has_vehicle,
        has_children=user.has_children
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"status": "success", "message": "Kayıt işlemi başarıyla tamamlandı.", "user_id": new_user.id}


# --- GİRİŞ YAP (LOGIN) GÜNCELLEMESİ ---
@router.post("/login", response_model=Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Kullanıcı girişi yapar ve JWT Token döndürür. (Swagger Authorize butonu ile uyumludur)
    """
    # form_data.username alanı, Swagger'ın standart formu gereği sabittir. Biz buraya email gireceğiz.
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-posta veya şifre hatalı."
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}