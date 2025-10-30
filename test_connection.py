import asyncio
import os
import sys
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

from database import engine, Base, get_db
from models import Task
from sqlalchemy import text

def test_connection():
    print("Проверка подключения к PostgreSQL через Supabase...")
    print(f"DATABASE_URL: {os.getenv('DATABASE_URL')[:30]}...")  # Показываем только начало URL
    
    try:
        # Пытаемся подключиться
        with engine.connect() as conn:
            # Выполняем простой SQL запрос
            result = conn.execute(text("SELECT 1"))
            print("✅ Подключение успешно!")
            print(f"Результат тестового запроса: {result.scalar()}")

        # Проверяем существование таблицы tasks
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'tasks'
                )
            """))
            table_exists = result.scalar()
            
            if table_exists:
                print("✅ Таблица 'tasks' существует")
                
                # Проверяем количество записей
                count_result = conn.execute(text("SELECT COUNT(*) FROM tasks"))
                task_count = count_result.scalar()
                print(f"✅ Количество задач в таблице: {task_count}")
            else:
                print("❌ Таблица 'tasks' не найдена")

        print("\n✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
        print("База данных готова к работе.")

    except Exception as e:
        print(f"\n❌ ОШИБКА ПОДКЛЮЧЕНИЯ:")
        print(f"Тип ошибки: {type(e).__name__}")
        print(f"Сообщение: {e}")
        print("\nПроверьте:")
        print("1. Правильно ли указан DATABASE_URL в .env")
        print("2. Доступен ли интернет")
        print("3. Работает ли Supabase проект")
        print("4. Создана ли таблица tasks в Supabase")

if __name__ == "__main__":
    test_connection()