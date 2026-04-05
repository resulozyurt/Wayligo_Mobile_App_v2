from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from models.trip import Trip, TripItem # TripItem eklendi
from models.trip import Trip
from models.user import User
from schemas.trip_schema import TripCreate, TripResponse, TripDetailResponse
from api.dependencies import get_current_user
from uuid import UUID

router = APIRouter()

@router.post("/", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
def create_trip(trip_data: TripCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # ... (Senin mevcut kodun tamamen aynı kalacak) ...
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
def get_my_trips(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    trips = db.query(Trip).filter(Trip.user_id == current_user.id).all()
    return trips

# --- YENİ EKLENEN ENDPOINT: Rotaya Mekan Ekleme ---
@router.post("/{trip_id}/items", status_code=status.HTTP_201_CREATED)
def add_poi_to_trip(
    trip_id: UUID, 
    poi_id: UUID, 
    order_index: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Oluşturulan rotaya manuel olarak bir mekan (POI) ekler.
    """
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Rota bulunamadı veya yetkiniz yok.")
    
    new_item = TripItem(trip_id=trip.id, poi_id=poi_id, order_index=order_index)
    db.add(new_item)
    db.commit()
    return {"status": "success", "message": "Mekan rotaya eklendi."}

# GÜNCELLENEN ENDPOINT: Detaylarda artık içindeki duraklar (items) da gelecek!
@router.get("/{trip_id}", response_model=TripDetailResponse) 
def get_trip_details(trip_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    
    if not trip:
        raise HTTPException(status_code=404, detail="Rota bulunamadı veya bu rotayı görme yetkiniz yok.")
        
    return trip