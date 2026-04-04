import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext

# Bcrypt motorumuz (Aynı kalıyor)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT İÇİN GİZLİ AYARLAR (İleride bunları .env dosyasına saklayacağız, şimdilik burada kalabilir)
SECRET_KEY = "wayligo_super_gizli_anahtar_kimseye_verme_123!" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # Biletin geçerlilik süresi: 1 Hafta (7 Gün)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# YENİ EKLENEN: VIP Bilet Üretme Fonksiyonu
def create_access_token(data: dict):
    to_encode = data.copy()
    # Biletin ne zaman süresinin dolacağını hesapla
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Gizli anahtarımızla bileti mühürle
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt