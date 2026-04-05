from fastapi import FastAPI
from core.database import engine, Base

#MODELS IMPORT LIST
from models import user, trip, poi
from api.v1.client import auth
from api.v1.client import users
from api.v1.client import trips
from api.v1.admin import pois
from api.v1.client import routes
from api.v1.client import pois as client_pois

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Wayligo API",
    description="Wayligo Projesi Backend Motoru",
    version="1.0.0"
)

app.include_router(auth.router, prefix="/api/v1/client/auth", tags=["Client Auth"])
app.include_router(users.router, prefix="/api/v1/client/users", tags=["Client Users"])
app.include_router(trips.router, prefix="/api/v1/client/trips", tags=["Client Trips"])
app.include_router(pois.router, prefix="/api/v1/admin/pois", tags=["Admin POIs"])
app.include_router(routes.router, prefix="/api/v1/client/routes", tags=["Client Routes"])
app.include_router(client_pois.router, prefix="/api/v1/client/pois", tags=["Client POI"])

@app.get("/")
def read_root():
    return {"status": "success", "message": "Wayligo Backend Sistemine Hoş Geldiniz! Motorlar çalışıyor."}

@app.get("/ping")
def ping_test():
    return {"ping": "pong", "info": "Sistem aktif ve istekleri dinliyor."}
