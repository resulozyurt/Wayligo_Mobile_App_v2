import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # --- Üçüncü Parti API Anahtarları ---
    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY")
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")
    REDIS_URL: str = os.getenv("REDIS_URL")
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    # --- JWT / Güvenlik ---
    # ARTIK KODDA GÖMÜLÜ DEĞİL: gizli anahtar yalnızca .env'den okunur.
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))

    # --- Uygulama Varsayılanları ---
    DEFAULT_LANGUAGE: str = os.getenv("DEFAULT_LANGUAGE", "tr")

    def validate(self) -> None:
        """
        Uygulama açılırken kritik anahtarların varlığını doğrular.
        SECRET_KEY yoksa sistem güvenli bir şekilde başlamayı reddeder (fail-fast).
        """
        if not self.SECRET_KEY:
            raise RuntimeError(
                "SECRET_KEY .env dosyasında tanımlı değil! "
                "Güvenlik nedeniyle uygulama başlatılamıyor. "
                "Üretmek için: python -c \"import secrets; print(secrets.token_urlsafe(64))\""
            )


settings = Settings()
settings.validate()