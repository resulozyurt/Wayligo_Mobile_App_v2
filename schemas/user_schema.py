from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

# Kullanıcı kayıt (Register) olurken bize göndereceği verilerin şeması
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr # Sadece geçerli bir e-posta formatını kabul eder (@ işareti vb.)
    username: str
    password: str # Bu şifreyi alıp, üstteki security.py ile hashleyeceğiz
    
    # Opsiyonel alanlar (Kullanıcı kayıt anında girmek zorunda değil)
    residence_city: Optional[str] = None
    has_vehicle: Optional[bool] = False
    has_children: Optional[bool] = False
    
    class Config:
        from_attributes = True

# Kullanıcı giriş yaparken bize göndereceği verilerin şeması
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Giriş başarılı olduğunda ona vereceğimiz VIP Biletin (Token) şeması
class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str # YENİ EKLENDİ

# Kullanıcı bilgilerini dışarı gönderirken (Response) kullanacağımız GÜVENLİ şema
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
    # DİKKAT: password_hash burada YOK! Dış dünyaya asla sızamaz.

class Config:
    from_attributes = True