from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import jwt  # PyJWT
import random
import uuid
from datetime import datetime, timedelta

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from core.database import get_db
from core.config import settings
from core.limiter import limiter
from core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
)
from models.user import User
from schemas.user_schema import (
    UserCreate,
    Token,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    RefreshTokenRequest,
    GoogleLoginRequest,
)
from services.email_service import send_otp_email

router = APIRouter()


# --- KAYIT OL (REGISTER) ---
@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
def register_user(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Bu e-posta adresi veya kullanıcı adı zaten sistemde kayıtlı.",
        )

    hashed_pw = get_password_hash(user.password)
    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        username=user.username,
        password_hash=hashed_pw,
        residence_city=user.residence_city,
        has_vehicle=user.has_vehicle,
        has_children=user.has_children,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"status": "success", "message": "Kayıt işlemi başarıyla tamamlandı.", "user_id": new_user.id}


# --- GİRİŞ YAP (LOGIN) ---
@router.post("/login", response_model=Token)
@limiter.limit("5/minute")  # Kaba kuvvet (brute force) saldırılarına karşı
def login_user(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == form_data.username).first()
    # Tek ve aynı mesaj: e-posta var mı yok mu sızdırmıyoruz.
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="E-posta veya şifre hatalı")

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token,
    }


# --- SESSİZ YENİLEME (SILENT REFRESH) ---
@router.post("/refresh", response_model=Token)
@limiter.limit("20/minute")
def refresh_access_token(
    request: Request,
    payload: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """
    Mobil uygulama, access token süresi dolunca arka planda çağırır.
    Refresh token verilir; yeni access + refresh token alınır.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Geçersiz yenileme bileti. Lütfen tekrar giriş yapın.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token_payload = jwt.decode(
            payload.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = token_payload.get("sub")
        token_type = token_payload.get("type")

        # Bu gerçekten bir 'refresh' token mı? (access token ile yenileme yapılamaz)
        if user_id is None or token_type != "refresh":
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    new_access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "refresh_token": new_refresh_token,
    }


# --- ŞİFREMİ UNUTTUM ---
@router.post("/forgot-password")
@limiter.limit("3/minute")  # OTP spam'ini engeller
def forgot_password(
    request: Request,
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == payload.email).first()

    # Hesap olsa da olmasa da TEK ve AYNI yanıt (enumeration saldırısını engeller).
    generic_message = {"message": "Eğer hesap mevcutsa, doğrulama kodu gönderildi."}

    if not user:
        return generic_message

    otp = str(random.randint(100000, 999999))
    user.otp_code = otp
    user.otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
    db.commit()

    # E-posta gönderimini arka plana atıyoruz -> kullanıcı yanıt için beklemez.
    background_tasks.add_task(send_otp_email, user.email, otp)

    return generic_message


# --- ŞİFRE SIFIRLAMA ---
@router.post("/reset-password")
@limiter.limit("5/minute")
def reset_password(
    request: Request,
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(
        User.email == payload.email,
        User.otp_code == payload.otp,
        User.otp_expires_at > datetime.utcnow(),
    ).first()

    if not user:
        raise HTTPException(status_code=400, detail="Kod hatalı veya süresi dolmuş.")

    user.password_hash = get_password_hash(payload.new_password)
    user.otp_code = None
    user.otp_expires_at = None
    db.commit()

    return {"message": "Şifreniz başarıyla güncellendi."}


# --- GOOGLE İLE GİRİŞ ---
@router.post("/google-login", response_model=Token)
@limiter.limit("10/minute")
def login_with_google(
    request: Request,
    payload: GoogleLoginRequest,
    db: Session = Depends(get_db),
):
    """
    Mobil uygulamadan gelen Google Identity Token'ı doğrular.
    Kullanıcı varsa giriş yapar, yoksa sessizce yeni hesap oluşturur.
    """
    try:
        id_info = id_token.verify_oauth2_token(
            payload.google_token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )

        email = id_info.get("email")
        first_name = id_info.get("given_name", "")
        last_name = id_info.get("family_name", "")

        user = db.query(User).filter(User.email == email).first()

        if not user:
            # BONUS DÜZELTME: username nullable=False & unique olduğundan
            # set edilmezse INSERT IntegrityError ile çökerdi. Otomatik üretiyoruz.
            base_username = (email.split("@")[0] if email else "user")[:20]
            unique_username = f"{base_username}_{uuid.uuid4().hex[:6]}"

            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                username=unique_username,
                # Sosyal girişte şifre yok; rastgele güçlü bir hash atıyoruz.
                password_hash=get_password_hash(str(uuid.uuid4())),
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "refresh_token": refresh_token,
        }

    except ValueError:
        raise HTTPException(status_code=401, detail="Geçersiz Google kimlik doğrulaması.")