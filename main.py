from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from core.database import engine, Base
from core.limiter import limiter  # Paylaşılan limiter örneği

# MODELS IMPORT LIST
from models import user, trip, poi, favorite, review
from api.v1.client import auth, users, trips, routes, favorites, reviews
from api.v1.client import pois as client_pois
from api.v1.admin import pois as admin_pois

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Wayligo API",
    description="Wayligo Projesi Backend Motoru",
    version="1.0.0",
)

# 1. HIZ SINIRLANDIRICI (RATE LIMITER)
# Limiter artık core/limiter.py'de; router'lar da AYNI örneği import eder.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 2. CORS GÜVENLİK DUVARI
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    # İleride: "https://www.wayligo.com"
    # Flutter mobil uygulaması origin göndermediği için varsayılan olarak geçer.
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


@app.get("/")
@limiter.limit("5/minute")
def read_root(request: Request):
    return {
        "status": "success",
        "message": "Wayligo Backend Sistemine Hoş Geldiniz! Güvenlik kalkanları devrede.",
    }


@app.get("/ping")
def ping_test():
    return {"ping": "pong", "info": "Sistem aktif ve istekleri dinliyor."}