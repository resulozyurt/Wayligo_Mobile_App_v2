from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from core.database import get_db
from services.map_service import get_directions
from services.poi_service import get_pois_along_route
from api.dependencies import get_current_user
from models.user import User

from core.ai_engine import generate_travel_plan
from schemas.trip_schema import TripCreate
from models.trip import Trip

router = APIRouter()


@router.get("/calculate")
async def calculate_route(
    origin: str,
    destination: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Google Maps rotasını hesaplar ve rota üzerindeki (15 km) mekanları bulur."""
    route_data = await get_directions(origin=origin, destination=destination)
    pois_on_route = get_pois_along_route(db=db, polyline=route_data["polyline"], radius_km=15)
    return {"route_info": route_data, "recommended_pois": pois_on_route}


@router.post("/generate-ai-plan")
async def generate_ai_route_plan(
    trip_data: TripCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Google'dan rotayı al
    route_data = await get_directions(
        origin=trip_data.start_location, destination=trip_data.destination_location
    )

    # 2. Rota üzerindeki mekanları bul
    pois_on_route = get_pois_along_route(db=db, polyline=route_data["polyline"], radius_km=15)

    # 3. AI için bağlam hazırla
    user_context = {
        "first_name": current_user.first_name,
        "has_children": current_user.has_children,
        "has_vehicle": current_user.has_vehicle,
        "residence_city": current_user.residence_city,
    }
    trip_details_dict = trip_data.model_dump(exclude={"start_date", "end_date"})
    trip_details_dict["start_date"] = str(trip_data.start_date)

    # 4. KRİTİK: generate_travel_plan SENKRON bir OpenAI çağrısıdır.
    #    Doğrudan await olmadan çağrılırsa, AI yanıtı beklenirken event loop
    #    (yani TÜM sunucu) kilitlenir. run_in_threadpool ile ayrı bir thread'e
    #    alıyoruz; sunucu bu sırada diğer istekleri işlemeye devam eder.
    ai_plan = await run_in_threadpool(
        generate_travel_plan,
        user_context,
        trip_details_dict,
        route_data,
        pois_on_route,
    )

    # 5. Veritabanına kaydet
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
        route_polyline=route_data["polyline"],
        ai_itinerary=ai_plan.model_dump(),
    )
    db.add(new_trip)
    db.commit()
    db.refresh(new_trip)

    return {
        "trip_id": new_trip.id,
        "route_polyline": new_trip.route_polyline,
        "ai_itinerary": new_trip.ai_itinerary,
    }