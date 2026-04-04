from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt
from core.database import get_db
from core.security import SECRET_KEY, ALGORITHM
from models.user import User

# Swagger'da sağ üstte o meşhur "Authorize" (Kilit) butonunu çıkaracak olan araç.
# Token'ı /login rotasından alacağını sisteme söylüyoruz.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/client/auth/login")

# İŞTE KİMİ KORUMALI ROTAMIZIN KAPISINDAKİ GÜVENLİK GÖREVLİSİ
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kimlik doğrulanamadı. Lütfen tekrar giriş yapın.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 1. Bileti (Token) çözüyoruz
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub") # İçine gizlediğimiz user_id'yi alıyoruz
        if user_id is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Oturum süresi doldu. Lütfen tekrar giriş yapın.")
    except jwt.PyJWTError:
        raise credentials_exception

    # 2. Bileti geçerli olan kişiyi veritabanında bul
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    # 3. Güvenlikten geçti, kullanıcıyı içeri al!
    return user

# YENİ EKLENEN: Sadece Admin'lerin geçebileceği ikinci güvenlik kapısı
def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu işlemi yapmak için yönetici (admin) yetkisine sahip olmalısınız."
        )
    return current_user