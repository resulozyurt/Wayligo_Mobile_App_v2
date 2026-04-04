import httpx
from fastapi import HTTPException
from core.config import settings

# async def kullanıyoruz çünkü FastAPI asenkrondur. 
# Google'dan cevap beklerken sunucunun diğer kullanıcıları bekletmemesi (kilitlenmemesi) gerekir.
async def get_directions(origin: str, destination: str):
    """
    Google Maps Directions API'ye bağlanıp iki nokta arasındaki mesafeyi,
    süreyi ve haritada çizilecek rotayı (Polyline) alır.
    """
    url = "https://maps.googleapis.com/maps/api/directions/json"
    
    # Google'a göndereceğimiz parametreler
    params = {
        "origin": origin,
        "destination": destination,
        "key": settings.GOOGLE_MAPS_API_KEY,
        "language": "tr" # Sonuçları (Örn: "10 saat 30 dakika") Türkçe almak için
    }
    
    # httpx ile Google'a asenkron bir HTTP isteği atıyoruz
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()
        
        # Eğer Google'dan "OK" dışında bir cevap gelirse (Örn: geçersiz şehir ismi)
        if data.get("status") != "OK":
            raise HTTPException(
                status_code=400, 
                detail=f"Rota hesaplanamadı. Şehir isimlerini kontrol edin. (Google Yanıtı: {data.get('status')})"
            )
            
        # Google'ın gönderdiği devasa JSON verisinden sadece bize lazım olanları (parse) ayıklıyoruz
        route = data["routes"][0]
        leg = route["legs"][0]
        
        return {
            "start_address": leg["start_address"],
            "end_address": leg["end_address"],
            "distance_text": leg["distance"]["text"], # Örn: "750 km"
            "distance_value": leg["distance"]["value"], # Örn: 750000 (Matematiksel işlemler için metre)
            "duration_text": leg["duration"]["text"], # Örn: "9 saat 15 dakika"
            "duration_value": leg["duration"]["value"], # Örn: 33300 (Matematiksel işlemler için saniye)
            
            # Polyline: Flutter uygulamasında haritaya mavi çizgiyi çizdirecek olan şifreli koordinat metni
            "polyline": route["overview_polyline"]["points"] 
        }