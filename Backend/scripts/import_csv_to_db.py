import pandas as pd
import asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Veritabanı bağlantı URL'si
DATABASE_URL = os.getenv("DATABASE_URL")

async def import_csv_to_db(csv_file_path):
    try:
        # CSV dosyasını oku
        df = pd.read_csv(csv_file_path, sep=';', encoding='utf-8')
        
        # Veritabanı bağlantısı
        engine = create_async_engine(DATABASE_URL)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as session:
            # Her satır için
            for _, row in df.iterrows():
                try:
                    # Veriyi hazırla
                    data = {
                        'asin': row['asin'],
                        'title': None,  # CSV'de title yok
                        'description': row['açıklama'],
                        'category': row['kategori'],
                        'ean': str(row['ean']),  # ean'i string'e çevir
                        'rank': str(row['rank']),  # rank'i string'e çevir
                        'sp1_stock': int(row['sp1_stock']),
                        'sp2_stock': int(row['sp2_stock']),
                        'created_at': datetime.now(),
                        'updated_at': datetime.now()
                    }
                    
                    # SQL sorgusu
                    query = text("""
                    INSERT INTO amazon_products2 
                    (asin, title, description, category, ean, rank, sp1_stock, sp2_stock, created_at, updated_at)
                    VALUES 
                    (:asin, :title, :description, :category, :ean, :rank, :sp1_stock, :sp2_stock, :created_at, :updated_at)
                    ON CONFLICT (asin) DO UPDATE SET
                        description = EXCLUDED.description,
                        category = EXCLUDED.category,
                        ean = EXCLUDED.ean,
                        rank = EXCLUDED.rank,
                        sp1_stock = EXCLUDED.sp1_stock,
                        sp2_stock = EXCLUDED.sp2_stock,
                        updated_at = CURRENT_TIMESTAMP
                    """)
                    
                    await session.execute(query, data)
                    await session.commit()
                    print(f"ASIN {row['asin']} başarıyla işlendi.")
                    
                except Exception as e:
                    print(f"Hata: ASIN {row['asin']} işlenirken hata oluştu: {str(e)}")
                    await session.rollback()
                    continue
        
        print("İşlem tamamlandı!")
        
    except Exception as e:
        print(f"Genel hata: {str(e)}")
    finally:
        await engine.dispose()

async def main():
    # CSV dosya yolunu kullanıcıdan al
    csv_file_path = input("CSV dosyasının tam yolunu girin: ")
    
    if not os.path.exists(csv_file_path):
        print("Hata: Dosya bulunamadı!")
        return
    
    await import_csv_to_db(csv_file_path)

if __name__ == "__main__":
    asyncio.run(main()) 