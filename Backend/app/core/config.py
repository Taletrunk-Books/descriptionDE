from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# .env dosyasını yükle
load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Amazon API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
        "extra": "allow"
    }

settings = Settings() 