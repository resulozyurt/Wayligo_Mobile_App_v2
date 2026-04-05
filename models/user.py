import uuid
from sqlalchemy import Column, String, Integer, Boolean, Date, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from core.database import Base

class User(Base):
    __tablename__ = "users" # Veritabanında tablonun adı bu olacak

    # UUID: Tahmin edilemez benzersiz kimlik (Sektör standardı)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Klasik Bilgiler
    first_name = Column(String, nullable=False) # nullable=False: Bu alan boş bırakılamaz zorunludur
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False) # unique=True: Aynı mailden iki tane olamaz
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False) # Şifreyi açık tutmuyoruz, hashlenmiş tutacağız
    
    # Demografik ve Araç Bilgileri
    birth_date = Column(Date, nullable=True) # Yaş hesabı için
    marital_status = Column(String, nullable=True) # 'single', 'married'
    has_children = Column(Boolean, default=False)
    has_vehicle = Column(Boolean, default=False)
    residence_city = Column(String, nullable=True)
    
    # Tatil Tercihleri (JSON formatında birden fazla değer tutabilmek için)
    travel_preferences = Column(JSONB, nullable=True)
    
    # Admin Paneli Yetkilendirmesi İçin Rol Sistemi
    role = Column(String, default="user") # Varsayılan olarak herkes 'user' olarak kayıt olur
    profile_image_url = Column(String, nullable=True)
    
    otp_code = Column(String, nullable=True) # 6 haneli kod
    otp_expires_at = Column(DateTime, nullable=True) # Son kullanma tarihi