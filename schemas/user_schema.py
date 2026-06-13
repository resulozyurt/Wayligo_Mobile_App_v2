from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID


# Kullanıcı kayıt (Register) şeması
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    username: str
    password: str

    residence_city: Optional[str] = None
    has_vehicle: Optional[bool] = False
    has_children: Optional[bool] = False

    class Config:
        from_attributes = True


# Kullanıcı giriş şeması
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Giriş sonrası dönen token paketi
class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


# Dışarı gönderilen GÜVENLİ kullanıcı şeması (password_hash burada YOK)
class UserResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    username: str
    residence_city: Optional[str] = None
    has_vehicle: Optional[bool] = None
    has_children: Optional[bool] = None
    role: str

    # DÜZELTİLDİ: Config artık doğru girintiyle UserResponse'un İÇİNDE.
    # Önceden modül seviyesindeydi; bu yüzden /me uçnoktası ORM nesnesini
    # döndüremiyor ve Pydantic v2 validation hatası veriyordu.
    class Config:
        from_attributes = True


# --- YENİ: Hassas verileri query string yerine BODY'de taşıyan şemalar ---
# (Şifre, OTP ve token'ların URL'e/loglara sızmasını engeller.)
class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class GoogleLoginRequest(BaseModel):
    google_token: str