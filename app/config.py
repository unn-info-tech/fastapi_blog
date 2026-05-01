from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    allowed_origins: str = "http://localhost:3000"
    environment: str = "development"   # ← YANGI
    debug: bool = True                 # ← YANGI
    

    # Email (ixtiyoriy)
    mail_username: str = ""
    mail_password: str = ""
    mail_from: str = ""
    mail_port: int = 587
    mail_server: str = "smtp.gmail.com"

    redis_url: str = "redis://localhost:6379"
    cache_ttl: int = 300    # 5 daqiqa (sekund)

    @property
    def origins_list(self):
        return [o.strip() for o in self.allowed_origins.split(",")]

    @property
    def is_production(self):
        return self.environment == "production"

    class Config:
        env_file = ".env"

settings = Settings()