from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Dict, Any
from datetime import datetime

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404:{"description":"task not found"}},
)

# Временное хранилище (позже будет заменено на PostgreSQL)
tasks_db: List[Dict[str, Any]] = [
    {
        "id": 1,
        "title": "Сдать проект по FastAPI",
        "description": "Завершить разработку API и написать документацию",
        "is_important": True,
        "is_urgent": True,
        "quadrant": "Q1",
        "completed": False,
        "created_at": datetime.now()
    },
    {
        "id": 2,
        "title": "Изучить SQLAlchemy",
        "description": "Прочитать документацию и попробовать примеры",
        "is_important": True,
        "is_urgent": False,
        "quadrant": "Q2",
        "completed": False,
        "created_at": datetime.now()
    },
    {
        "id": 3,
        "title": "Сходить на лекцию",
        "description": None,
        "is_important": False,
        "is_urgent": True,
        "quadrant": "Q3",
        "completed": False,
        "created_at": datetime.now()
    },
    {
        "id": 4,
        "title": "Посмотреть сериал",
        "description": "Новый сезон любимого сериала",
        "is_important": False,
        "is_urgent": False,
        "quadrant": "Q4",
        "completed": True,
        "created_at": datetime.now()
    },
]

@router.get("/tasks")
async def get_all_tasks() -> dict:
    return {
        "count": len(tasks_db),
        "tasks": tasks_db
    }

# ВАЖНО: Специфичные пути должны быть объявлены ПЕРЕД динамическими путями

@router.get("/tasks/search")
async def search_tasks(q: str = Query(..., min_length=2, description="Ключевое слово для поиска")) -> dict:
    """
    Поиск задач по ключевому слову в названии или описании
    """
    # Поиск не зависит от регистра
    search_term = q.lower()
    
    # Фильтруем задачи, где ключевое слово встречается в title или description
    filtered_tasks = [
        task for task in tasks_db
        if (task["title"] and search_term in task["title"].lower()) or
           (task["description"] and search_term in task["description"].lower())
    ]
    
    return {
        "query": q,
        "count": len(filtered_tasks),
        "tasks": filtered_tasks
    }

@router.get("/tasks/stats")
async def get_tasks_stats() -> dict:
    """
    Получить статистику по задачам
    """
    # Общее количество задач
    total_tasks = len(tasks_db)
    
    # Статистика по квадрантам
    by_quadrant = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}
    for task in tasks_db:
        quadrant = task["quadrant"]
        if quadrant in by_quadrant:
            by_quadrant[quadrant] += 1
    
    # Статистика по статусу выполнения
    completed = sum(1 for task in tasks_db if task["completed"])
    pending = total_tasks - completed
    
    return {
        "total_tasks": total_tasks,
        "by_quadrant": by_quadrant,
        "by_status": {
            "completed": completed,
            "pending": pending
        }
    }

@router.get("/tasks/status/{status}")
async def get_tasks_by_status(status: str) -> dict:
    """
    Получить задачи по статусу выполнения
    """
    # Валидация статуса
    if status not in ["completed", "pending"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Статус не найден. Используйте: 'completed' или 'pending'"
        )
    
    # Определяем булево значение для фильтрации
    is_completed = status == "completed"
    
    # Фильтруем задачи
    filtered_tasks = [
        task for task in tasks_db 
        if task["completed"] == is_completed
    ]
    
    return {
        "status": status,
        "count": len(filtered_tasks),
        "tasks": filtered_tasks
    }

@router.get("/tasks/quadrant/{quadrant}")
async def get_tasks_by_quadrant(quadrant: str) -> dict:
    if quadrant not in ["Q1", "Q2", "Q3", "Q4"]:
        raise HTTPException(status_code=400, detail="Неверный квадрант. Используйте: Q1, Q2, Q3, Q4")
    
    filtered_tasks = [
        task
        for task in tasks_db
        if task["quadrant"] == quadrant
    ]
    return {
        "quadrant": quadrant,
        "count": len(filtered_tasks),
        "tasks": filtered_tasks
    }

@router.get("/tasks/{task_id}")
async def get_task_by_id(task_id: int) -> dict:
    """
    Получить задачу по ID
    """
    task = next((task for task in tasks_db if task["id"] == task_id), None)
    
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Задача с ID {task_id} не найдена"
        )
    
    return task