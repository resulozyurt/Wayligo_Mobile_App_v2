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

settings = Settings()