from sqlalchemy.orm import Session
from sqlalchemy import text
from core.config import settings


def get_pois_along_route(db: Session, polyline: str, radius_km: int = 15, lang: str = None):
    """
    Google'ın encoded polyline'ını kullanarak, rota çizgisine 'radius_km'
    mesafesindeki mekanları bulur. Dil parametriktir (varsayılan .env DEFAULT_LANGUAGE).
    """
    lang = lang or settings.DEFAULT_LANGUAGE

    # Not: dil filtresi WHERE yerine JOIN ON içinde -> gerçek LEFT JOIN.
    # Böylece çevirisi olmayan mekan yine listede (name=NULL ile) gelir, sessizce düşmez.
    sql_query = text("""
        SELECT p.id, p.latitude, p.longitude, p.category, pt.name, pt.description
        FROM pois p
        LEFT JOIN poi_translations pt
            ON p.id = pt.poi_id AND pt.language_code = :lang
        WHERE ST_DWithin(
            p.geom::geography,
            ST_LineFromEncodedPolyline(:polyline, 5)::geography,
            :radius_meters
        )
    """)

    result = db.execute(sql_query, {
        "polyline": polyline,
        "radius_meters": radius_km * 1000,
        "lang": lang,
    })

    pois = []
    for row in result:
        pois.append({
            "id": str(row.id),
            "name": row.name,
            "category": row.category,
            "latitude": row.latitude,
            "longitude": row.longitude,
            "description": row.description,
        })

    return pois


def get_nearby_pois(db: Session, lat: float, lng: float, radius_km: int = 5, lang: str = None):
    """
    Kullanıcının anlık konumuna göre yarıçap içindeki mekanları,
    en yakından en uzağa sıralı döndürür (PostGIS ST_DWithin + ST_Distance).
    """
    lang = lang or settings.DEFAULT_LANGUAGE

    sql_query = text("""
        SELECT p.id, p.category, p.latitude, p.longitude, pt.name, pt.description,
               ST_Distance(
                   p.geom::geography,
                   ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography
               ) AS distance_meters
        FROM pois p
        LEFT JOIN poi_translations pt
            ON p.id = pt.poi_id AND pt.language_code = :lang
        WHERE ST_DWithin(
            p.geom::geography,
            ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography,
            :radius_meters
        )
        ORDER BY distance_meters ASC
    """)

    result = db.execute(sql_query, {
        "lat": lat,
        "lng": lng,
        "radius_meters": radius_km * 1000,
        "lang": lang,
    })

    pois = []
    for row in result:
        pois.append({
            "id": str(row.id),
            "name": row.name,
            "category": row.category,
            "latitude": row.latitude,
            "longitude": row.longitude,
            "description": row.description,
            "distance_km": round(row.distance_meters / 1000, 2),
        })

    return pois