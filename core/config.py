# core/config.py güncellenmiş hali
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    # YENİ EKLENENLER
    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY")
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")
    REDIS_URL: str = os.getenv("REDIS_URL")

settings = Settings()