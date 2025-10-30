from fastapi import FastAPI
from routers import tasks, stats
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Просто запускаем приложение, не инициализируем БД
    # (таблицы уже созданы в Supabase)
    logger.info("🚀 Starting Task Management API")
    yield
    logger.info("🛑 Shutting down Task Management API")

app = FastAPI(
    title="Task Management API",
    description="API для управления задачами. Косоуров Артем",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Подключаем роутеры с префиксом /api/v1
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(stats.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Добро пожаловать в Task Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "api_base": "/api/v1"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API работает корректно"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)