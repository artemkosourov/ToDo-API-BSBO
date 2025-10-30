from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator
import os
from dotenv import load_dotenv

load_dotenv()

# Используем синхронное подключение (убираем +asyncpg)
DATABASE_URL = os.getenv("DATABASE_URL").replace("+asyncpg", "")

# Синхронный engine
engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator:
    """
    Зависимость для получения сессии БД.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def calculate_quadrant(is_important: bool, is_urgent: bool) -> str:
    """Вычисляет квадрант матрицы Эйзенхауэра"""
    if is_important and is_urgent:
        return "Q1"
    elif is_important and not is_urgent:
        return "Q2"
    elif not is_important and is_urgent:
        return "Q3"
    else:
        return "Q4"