from openai import OpenAI
from pydantic import BaseModel
from typing import List
from core.config import settings

# OpenAI motorumuzu gizli anahtarımızla ateşliyoruz
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# --- YAPAY ZEKA İÇİN KESİN ÇIKTI ŞEMALARI (STRUCTURED OUTPUTS) ---
# Yapay zeka bu şemaların dışına ASLA çıkamayacak.

class ItineraryStop(BaseModel):
    time: str # Örn: "10:30"
    location_name: str # Örn: "Amasya Lezzet Durağı" veya "Çorum Yol Ayrımı"
    action: str # Örn: "Öğle Yemeği", "Çocuklar için Mola", "Yakıt İkmali"
    description: str # Neden burası seçildi? Uzun açıklama.
    duration_minutes: int

class TravelPlan(BaseModel):
    trip_title: str # Örn: "Samsun'dan Adana'ya Keyifli Aile Rotası"
    total_estimated_duration: str
    summary: str # Yolculuğun genel özeti ve dikkat edilecekler
    itinerary: List[ItineraryStop] # Yukarıdaki durakların bir listesi

def generate_travel_plan(user_context: dict, trip_details: dict, route_info: dict, pois: list) -> TravelPlan:
    """
    Kullanıcı verilerini, rota bilgisini ve mekanları alıp OpenAI'a gönderir.
    Sistem bize %100 'TravelPlan' formatında bir JSON döndürür.
    """
    
    # 1. AI'a Kim Olduğunu Söylüyoruz (Sistem Promptu)
    system_prompt = (
        "Sen Wayligo adında, dünya standartlarında bir Seyahat Mühendisi ve Rota Planlama Zekasısın. "
        "Sana verilen kullanıcı profilini, yolculuk detaylarını, Google Maps rota mesafesini "
        "ve güzergah üzerindeki mekanları (POIs) analiz edip, saat saat planlanmış kusursuz bir seyahat rotası çıkaracaksın. "
        "Kullanıcının çocuk durumu, araç durumu ve mola tercihlerini mutlaka hesaba kat. "
        "Güzergah üzerindeki POI'leri mantıklı saatlerde plana dahil et. "
        "Yanıtın KESİNLİKLE JSON formatında ve beklenen şemaya uygun olmalıdır."
    )

    # 2. Elimizdeki Verileri AI'a Sunuyoruz (Kullanıcı Promptu)
    user_prompt = f"""
    KULLANICI PROFİLİ: {user_context}
    YOLCULUK BİLGİLERİ (İstekler): {trip_details}
    GOOGLE MAPS (Otoyol Bilgisi): Toplam Mesafe: {route_info.get('distance_text')}, Tahmini Süre: {route_info.get('duration_text')}
    GÜZERGAHTAKİ MEKANLAR (Kullanabileceğin POI'ler): {pois}
    
    Lütfen bu verilere dayanarak yola çıkış saatinden varış saatine kadar mantıklı durakları içeren bir plan oluştur.
    """

    # 3. Zekayı Çalıştırıyoruz (parse metodu ile Structured Output alıyoruz)
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format=TravelPlan # İşte o sihirli kısım! AI sadece bu formata uymak zorunda.
    )

    # Gelen yapılandırılmış (parse edilmiş) nesneyi geri döndürüyoruz
    return response.choices[0].message.parsed