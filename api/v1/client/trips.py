from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from models.trip import Trip
from models.user import User
from schemas.trip_schema import TripCreate, TripResponse
from api.dependencies import get_current_user

router = APIRouter()

@router.post("/", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
def create_trip(
    trip_data: TripCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user) # GÜVENLİK: Kullanıcı giriş yapmış olmalı!
):
    """
    Giriş yapmış kullanıcı için yeni bir tatil planı (Trip) oluşturur.
    """
    # Gelen veriyi veritabanı modeline dönüştür
    # DİKKAT: user_id değerini dışarıdan (frontend'den) DEĞİL, token'dan (current_user) alıyoruz!
    new_trip = Trip(
        user_id=current_user.id,
        start_location=trip_data.start_location,
        destination_location=trip_data.destination_location,
        start_date=trip_data.start_date,
        end_date=trip_data.end_date,
        transportation_type=trip_data.transportation_type,
        companion_type=trip_data.companion_type,
        trip_concept=trip_data.trip_concept,
        allow_route_deviations=trip_data.allow_route_deviations,
        break_preference=trip_data.break_preference,
        needs_hotel_rec=trip_data.needs_hotel_rec
    )

    db.add(new_trip)
    db.commit()
    db.refresh(new_trip)

    return new_trip

@router.get("/", response_model=list[TripResponse])
def get_my_trips(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Kullanıcının daha önce oluşturduğu tüm tatil planlarını listeler.
    """
    # Sadece bu kullanıcıya ait olan rotaları getir
    trips = db.query(Trip).filter(Trip.user_id == current_user.id).all()
    return trips

@router.get("/{trip_id}", response_model=TripResponse)
def get_trip_details(
    trip_id: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Belirli bir tatil planının tüm detaylarını (Yapay Zeka planı dahil) getirir.
    Güvenlik: Sadece rotayı oluşturan kişi bu detayları görebilir.
    """
    trip = db.query(Trip).filter(
        Trip.id == trip_id, 
        Trip.user_id == current_user.id # Başkasının rotasına bakmasını engelliyoruz
    ).first()
    
    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Rota bulunamadı veya bu rotayı görme yetkiniz yok."
        )
        
    return trip