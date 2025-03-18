from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.endpoints import amazon
from app.db.base import Base, engine
import asyncio

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tüm originlere izin ver
    allow_credentials=True,
    allow_methods=["*"],  # Tüm HTTP metodlarına izin ver
    allow_headers=["*"],  # Tüm headerlara izin ver
)

# API router'ları
app.include_router(amazon.router, prefix=settings.API_V1_STR, tags=["amazon"])

@app.get("/")
async def root():
    return {"message": "Amazon API çalışıyor"}

@app.on_event("startup")
async def startup_event():
    # Veritabanı tablolarını oluştur
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("shutdown")
async def shutdown_event():
    # Veritabanı bağlantısını kapat
    await engine.dispose()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        workers=4,  # Worker sayısı
        loop="uvloop",  # Daha hızlı event loop
        limit_concurrency=1000,  # Maksimum eşzamanlı bağlantı
        backlog=2048,  # Bekleyen bağlantı sayısı
        timeout_keep_alive=30,  # Keep-alive timeout
        reload=True  # Geliştirme için hot reload
    ) 