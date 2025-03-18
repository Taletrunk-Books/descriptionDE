from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# .env dosyasını yükle
load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Amazon Description API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Veritabanı URL'sini .env dosyasından al
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    class Config:
        case_sensitive = True

settings = Settings() 