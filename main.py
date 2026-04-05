from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from core.database import engine, Base

# MODELS IMPORT LIST
from models import user, trip, poi, favorite, review
from api.v1.client import auth, users, trips, routes, favorites, reviews
from api.v1.client import pois as client_pois
from api.v1.admin import pois as admin_pois

Base.metadata.create_all(bind=engine)

# 1. HIZ SINIRLANDIRICIYI (RATE LIMITER) BAŞLATIYORUZ
# get_remote_address: İstek atan kişinin IP adresini alır ve ona göre sınır koyar
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Wayligo API",
    description="Wayligo Projesi Backend Motoru",
    version="1.0.0"
)

# Hız sınırını aşanlara gösterilecek hata mesajını FastAPI'ye tanıtıyoruz
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 2. CORS GÜVENLİK DUVARI (Hangi siteler/uygulamalar bize istek atabilir?)
origins = [
    "http://localhost:3000", # Eğer web paneli yaparsan (React vb.)
    "http://127.0.0.1:3000",
    # İleride "https://www.wayligo.com" gibi canlı domainlerini buraya ekleyeceksin.
    # Flutter mobil uygulaması origin göndermediği için varsayılan olarak geçer.
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Tüm GET, POST, PUT, DELETE işlemlerine izin ver
    allow_headers=["*"], # Tüm güvenlik başlıklarına (Token vb.) izin ver
)

# ROUTER'LARI SİSTEME DAHİL ETME
app.include_router(auth.router, prefix="/api/v1/client/auth", tags=["Client Auth"])
app.include_router(users.router, prefix="/api/v1/client/users", tags=["Client Users"])
app.include_router(trips.router, prefix="/api/v1/client/trips", tags=["Client Trips"])
app.include_router(admin_pois.router, prefix="/api/v1/admin/pois", tags=["Admin POIs"])
app.include_router(routes.router, prefix="/api/v1/client/routes", tags=["Client Routes"])
app.include_router(client_pois.router, prefix="/api/v1/client/pois", tags=["Client POI"])
app.include_router(favorites.router, prefix="/api/v1/client/favorites", tags=["Client Favorites"])
app.include_router(reviews.router, prefix="/api/v1/client/reviews", tags=["Client Reviews"])

# 3. GLOBAL HIZ SINIRI TESTİ (Örn: Dakikada en fazla 5 istek)
@app.get("/")
@limiter.limit("5/minute") # Dakikada 5 istekle sınırlandırdık!
def read_root(request: Request):
    return {"status": "success", "message": "Wayligo Backend Sistemine Hoş Geldiniz! Güvenlik kalkanları devrede."}

@app.get("/ping")
def ping_test():
    return {"ping": "pong", "info": "Sistem aktif ve istekleri dinliyor."}