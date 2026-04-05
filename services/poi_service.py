from sqlalchemy.orm import Session
from sqlalchemy import text

def get_pois_along_route(db: Session, polyline: str, radius_km: int = 15):
    """
    Google'ın Polyline metnini kullanarak, rota çizgisine 'radius_km' mesafesindeki mekanları bulur.
    """
    # PostGIS'in sihirli fonksiyonlarıyla doğrudan veritabanında coğrafi arama yapıyoruz.
    # geom::geography diyerek mesafeyi derece değil "metre" cinsinden hesaplamasını sağlıyoruz.
    sql_query = text("""
        SELECT p.id, p.latitude, p.longitude, p.category, pt.name, pt.description
        FROM pois p
        LEFT JOIN poi_translations pt ON p.id = pt.poi_id
        WHERE ST_DWithin(
            p.geom::geography, 
            ST_LineFromEncodedPolyline(:polyline, 5)::geography, 
            :radius_meters
        ) AND pt.language_code = 'tr'
    """)
    
    # 15 km'yi metreye (15000) çevirip sorguyu çalıştırıyoruz
    result = db.execute(sql_query, {
        "polyline": polyline, 
        "radius_meters": radius_km * 1000
    })
    
    # Gelen SQL sonucunu API'nin anlayacağı JSON dostu bir listeye çeviriyoruz
    pois = []
    for row in result:
        pois.append({
            "id": str(row.id),
            "name": row.name,
            "category": row.category,
            "latitude": row.latitude,
            "longitude": row.longitude,
            "description": row.description
        })
    
    return pois

def get_nearby_pois(db: Session, lat: float, lng: float, radius_km: int = 5):
    """
    Kullanıcının anlık konumuna göre belirtilen yarıçap (km) içindeki mekanları bulur.
    PostGIS'in ST_Distance ve ST_DWithin fonksiyonlarını kullanarak ışık hızında 
    en yakından en uzağa doğru sıralar.
    """
    sql_query = text("""
        SELECT p.id, p.category, p.latitude, p.longitude, pt.name, pt.description,
               ST_Distance(p.geom::geography, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography) as distance_meters
        FROM pois p
        LEFT JOIN poi_translations pt ON p.id = pt.poi_id
        WHERE ST_DWithin(
            p.geom::geography, 
            ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography, 
            :radius_meters
        ) AND pt.language_code = 'tr'
        ORDER BY distance_meters ASC
    """)
    
    result = db.execute(sql_query, {
        "lat": lat,
        "lng": lng,
        "radius_meters": radius_km * 1000 # Kilometreyi metreye çeviriyoruz
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
            "distance_km": round(row.distance_meters / 1000, 2) # Örn: 1.45 km
        })
    
    return pois