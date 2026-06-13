from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from core.database import get_db
from core.config import settings
from models.trip import Trip, TripItem
from models.poi import POI, POITranslation
from models.user import User
from schemas.trip_schema import TripCreate, TripResponse, TripDetailResponse, TripItemResponse
from api.dependencies import get_current_user
from uuid import UUID

router = APIRouter()


@router.post("/", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
def create_trip(
    trip_data: TripCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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
        needs_hotel_rec=trip_data.needs_hotel_rec,
    )
    db.add(new_trip)
    db.commit()
    db.refresh(new_trip)
    return new_trip


@router.get("/", response_model=list[TripResponse])
def get_my_trips(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    trips = (
        db.query(Trip)
        .filter(Trip.user_id == current_user.id)
        .order_by(Trip.id)  # NOT: kronolojik sıra için Trip'e created_at eklenmesi önerilir
        .offset(offset)
        .limit(limit)
        .all()
    )
    return trips


@router.post("/{trip_id}/items", status_code=status.HTTP_201_CREATED)
def add_poi_to_trip(
    trip_id: UUID,
    poi_id: UUID,
    order_index: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Oluşturulan rotaya manuel olarak bir mekan (POI) ekler."""
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Rota bulunamadı veya yetkiniz yok.")

    # Eklenmek istenen mekan gerçekten var mı? (ForeignKey hatasını dostça yakala)
    poi = db.query(POI).filter(POI.id == poi_id).first()
    if not poi:
        raise HTTPException(status_code=404, detail="Eklenmek istenen mekan bulunamadı.")

    new_item = TripItem(trip_id=trip.id, poi_id=poi_id, order_index=order_index)
    db.add(new_item)
    db.commit()
    return {"status": "success", "message": "Mekan rotaya eklendi."}


@router.get("/{trip_id}", response_model=TripDetailResponse)
def get_trip_details(
    trip_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not trip:
        raise HTTPException(
            status_code=404, detail="Rota bulunamadı veya bu rotayı görme yetkiniz yok."
        )

    # Durakları POI bilgisiyle TEK sorguda, sıralı çekiyoruz (N+1 yok).
    rows = (
        db.query(TripItem, POI, POITranslation)
        .join(POI, TripItem.poi_id == POI.id)
        .outerjoin(
            POITranslation,
            (POITranslation.poi_id == POI.id)
            & (POITranslation.language_code == settings.DEFAULT_LANGUAGE),
        )
        .filter(TripItem.trip_id == trip.id)
        .order_by(TripItem.order_index.asc())
        .all()
    )

    items = [
        TripItemResponse(
            id=item.id,
            trip_id=item.trip_id,
            poi_id=item.poi_id,
            order_index=item.order_index,
            poi_name=translation.name if translation else None,
            poi_category=poi.category,
            latitude=poi.latitude,
            longitude=poi.longitude,
        )
        for item, poi, translation in rows
    ]

    # Trip alanlarını ORM'den oku, zenginleştirilmiş items'ı elle ekle.
    response = TripDetailResponse.model_validate(trip)
    response.items = items
    return response