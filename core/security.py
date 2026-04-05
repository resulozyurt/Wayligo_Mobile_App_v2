from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext

# Kendi gizli anahtarını buraya koyduğundan emin ol
SECRET_KEY = "2WVa50YuVhVEMC3PKEAYVtAFS6et3bobDGUsEV5hts1hRi9HH9oWYRrxFXXzGtaw" 
ALGORITHM = "HS256"

# PROFESYONEL STANDARTLAR
ACCESS_TOKEN_EXPIRE_MINUTES = 15 # Ana biletin ömrü 15 dakikaya düştü!
REFRESH_TOKEN_EXPIRE_DAYS = 30   # Yenileme biletinin ömrü 30 gün

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"}) # Tipini belirttik
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- YENİ EKLENEN FONSİYON: REFRESH TOKEN ÜRETİCİ ---
def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"}) # Bunun bir refresh token olduğunu belirtiyoruz
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt