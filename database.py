from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from config import settings

# 환경별 설정에서 데이터베이스 URL을 가져옵니다
DATABASE_URL = settings.database_url
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()