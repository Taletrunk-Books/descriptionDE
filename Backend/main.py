from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.endpoints import amazon
from app.db.base import Base, engine
from contextlib import asynccontextmanager
import uvicorn
import logging

# Logging ayarları
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Başlangıçta çalışacak kodlar
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Veritabanı tabloları başarıyla oluşturuldu")
        yield
    except Exception as e:
        logger.error(f"Başlangıç hatası: {str(e)}")
        raise
    finally:
        # Kapanışta çalışacak kodlar
        await engine.dispose()
        logger.info("Veritabanı bağlantısı kapatıldı")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
    debug=True  # Debug modunu aktif et
)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tüm originlere izin ver
    allow_credentials=True,
    allow_methods=["*"],  # Tüm HTTP metodlarına izin ver
    allow_headers=["*"],  # Tüm headerlara izin ver
    expose_headers=["*"]  # Tüm headerları expose et
)

# API router'ları
app.include_router(amazon.router, prefix=settings.API_V1_STR, tags=["amazon"])

@app.get("/")
async def root():
    return {"message": "Amazon API çalışıyor"}

def start():
    """Uygulamayı başlat"""
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        workers=1,
        limit_concurrency=1000,
        backlog=2048,
        timeout_keep_alive=30,
        reload=True,
        log_level="debug"  # Log seviyesini debug yap
    )

if __name__ == "__main__":
    start() 