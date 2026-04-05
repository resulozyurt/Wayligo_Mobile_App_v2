from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import verify_password, get_password_hash, create_access_token, create_refresh_token # Ekledik
from models.user import User
from schemas.user_schema import UserCreate, UserResponse, Token
from jose import jwt, JWTError # Token çözmek için
from core.security import SECRET_KEY, ALGORITHM
import random
from datetime import datetime, timedelta
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from core.config import settings
import uuid

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
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="E-posta veya şifre hatalı")
    
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="E-posta veya şifre hatalı")
    
    # 1. Ana bileti üret (15 Dakika)
    access_token = create_access_token(data={"sub": str(user.id)})
    
    # 2. Yenileme biletini üret (30 Gün)
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # 3. İkisini birden teslim et
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "refresh_token": refresh_token
    }

# --- YENİ EKLENEN: SESSİZ YENİLEME KAPISI ---
@router.post("/refresh", response_model=Token)
def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    """
    Mobil uygulama tarafından, ana token süresi bittiğinde arka planda çağrılır.
    Eski refresh_token verilir, yepyeni bir access_token ve refresh_token alınır.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Geçersiz yenileme bileti. Lütfen tekrar giriş yapın.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Gelen token'ı çöz
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        # Bu token gerçekten bir "refresh" token mı diye kontrol et (Güvenlik)
        if user_id is None or token_type != "refresh":
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
        
    # Kullanıcı veritabanında hala duruyor mu? (Belki hesabı silindi/banlandı)
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
        
    # Her şey yolundaysa, yepyeni biletleri üret ve ver
    new_access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "refresh_token": new_refresh_token
    }

@router.post("/forgot-password")
def forgot_password(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Güvenlik nedeniyle "Kullanıcı yok" demiyoruz, hep aynı mesajı veriyoruz
        return {"message": "Eğer hesap mevcutsa, doğrulama kodu gönderildi."}

    # 1. 6 haneli rastgele kod üret
    otp = str(random.randint(100000, 999999))
    
    # 2. Veritabanına kaydet (10 dakika ömür ver)
    user.otp_code = otp
    user.otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
    db.commit()

    # 3. E-postayı gönder
    from services.email_service import send_otp_email
    send_otp_email(user.email, otp)
    
    return {"message": "Doğrulama kodu e-posta adresinize gönderildi."}

@router.post("/reset-password")
def reset_password(email: str, otp: str, new_password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        User.email == email, 
        User.otp_code == otp,
        User.otp_expires_at > datetime.utcnow()
    ).first()

    if not user:
        raise HTTPException(status_code=400, detail="Kod hatalı veya süresi dolmuş.")

    # Şifreyi güncelle ve OTP'yi temizle
    user.password_hash = get_password_hash(new_password)
    user.otp_code = None
    user.otp_expires_at = None
    db.commit()

    return {"message": "Şifreniz başarıyla güncellendi."}

@router.post("/google-login", response_model=Token)
def login_with_google(google_token: str, db: Session = Depends(get_db)):
    """
    Mobil uygulamadan gelen Google Identity Token'ı doğrular.
    Kullanıcı varsa giriş yapar, yoksa sessizce yeni hesap oluşturur.
    """
    try:
        # 1. Token'ı Google sunucularında doğrula
        id_info = id_token.verify_oauth2_token(
            google_token, 
            google_requests.Request(), 
            settings.GOOGLE_CLIENT_ID
        )

        # 2. Google'dan kullanıcının bilgilerini al
        email = id_info.get("email")
        first_name = id_info.get("given_name", "")
        last_name = id_info.get("family_name", "")

        # 3. Bu e-posta ile kayıtlı kullanıcımız var mı?
        user = db.query(User).filter(User.email == email).first()

        # 4. Kullanıcı yoksa, sessizce (şifresiz) veritabanına kaydet!
        if not user:
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                # Sosyal giriş yapanların şifresi olmaz, rastgele karmaşık bir şifre atıyoruz
                password_hash=get_password_hash(str(uuid.uuid4())), 
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # 5. Artık kullanıcımız olduğuna göre, Wayligo'nun kendi biletlerini üret
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "refresh_token": refresh_token
        }

    except ValueError:
        # Geçersiz veya sahte bir Google token geldiğinde
        raise HTTPException(status_code=401, detail="Geçersiz Google kimlik doğrulaması.")