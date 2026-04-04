import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY")
    # YENİ EKLENDİ
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")

settings = Settings()