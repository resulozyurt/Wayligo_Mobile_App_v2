import redis
from core.config import settings

# Eğer .env dosyasında REDIS_URL tanımlanmışsa bağlantıyı kur, yoksa None dön (Geliştirici dostu yapı)
if settings.REDIS_URL:
    # decode_responses=True çok önemlidir: Gelen veriyi makine dilinden (bytes) çıkarıp doğrudan string (metin) yapar
    redis_db = redis.from_url(settings.REDIS_URL, decode_responses=True)
else:
    redis_db = None

def get_redis():
    """
    Uygulama içinde Redis'i çağırmak için kullanacağımız bağımlılık (Dependency) fonksiyonu.
    """
    return redis_db