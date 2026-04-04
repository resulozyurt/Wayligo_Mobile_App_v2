from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Bu bizim veritabanı bağlantı cümlemiz (Connection String).
# Şimdilik örnek olarak bırakıyoruz, birazdan gerçeğiyle değiştireceğiz.
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Pf2XY1uakyYhCtVtp0@db.ookxzlarimfeqpyvqncs.supabase.co:5432/postgres"

# Veritabanı motorumuzu (engine) oluşturuyoruz.
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Veritabanı ile konuşacak oturum (session) fabrikasını kuruyoruz.
# autocommit=False: Her işlemi anında kaydetme, emin olunca biz onaylayalım (güvenlik için).
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tablo modellerimiz için temel sınıf (Base class). 
# Tüm veritabanı tablolarımız bu sınıftan miras alacak.
Base = declarative_base()

# API istekleri geldiğinde veritabanı kapısını açıp, işlem bitince kapatacak fonksiyon.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()