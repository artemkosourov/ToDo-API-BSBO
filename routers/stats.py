from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import date, timedelta
from database import get_db
from models import Task

router = APIRouter(
    prefix="/stats",
    tags=["statistics"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def get_tasks_stats(db: Session = Depends(get_db)) -> dict:
    # Общее количество задач
    total_tasks = db.query(Task).count()
    
    # Задачи по квадрантам
    quadrant_result = db.query(Task.quadrant, func.count(Task.id)).group_by(Task.quadrant).all()
    by_quadrant = dict(quadrant_result)
    
    # Завершенные и ожидающие задачи
    completed = db.query(Task).filter(Task.completed == True).count()
    pending = total_tasks - completed
    
    # Важные и срочные задачи
    important_tasks = db.query(Task).filter(Task.is_important == True).count()
    urgent_tasks = db.query(Task).filter(Task.is_urgent == True).count()
    
    # Задачи с датой завершения
    completed_with_date = db.query(Task).filter(Task.completed_at.isnot(None)).count()
    
    # НОВАЯ СТАТИСТИКА: По дедлайнам
    today = date.today()
    
    # Задачи с дедлайнами
    tasks_with_deadline = db.query(Task).filter(Task.deadline.isnot(None)).count()
    
    # Просроченные задачи
    overdue_tasks = db.query(Task).filter(
        Task.deadline.isnot(None),
        Task.deadline < today,
        Task.completed == False
    ).count()
    
    # Предстоящие дедлайны (в течение 7 дней)
    upcoming_deadlines = db.query(Task).filter(
        Task.deadline.isnot(None),
        Task.deadline >= today,
        Task.deadline <= today + timedelta(days=7),
        Task.completed == False
    ).count()
    
    return {
        "total_tasks": total_tasks,
        "by_quadrant": by_quadrant,
        "by_status": {
            "completed": completed,
            "pending": pending
        },
        "by_priority": {
            "important": important_tasks,
            "urgent": urgent_tasks
        },
        "analytics": {
            "completed_with_date": completed_with_date,
            "completion_rate": round((completed / total_tasks) * 100, 2) if total_tasks > 0 else 0
        },
        # НОВАЯ СТАТИСТИКА
        "deadline_stats": {
            "tasks_with_deadline": tasks_with_deadline,
            "overdue_tasks": overdue_tasks,
            "upcoming_deadlines": upcoming_deadlines,
            "tasks_without_deadline": total_tasks - tasks_with_deadline
        }
    }

@router.get("/quadrant-distribution")
async def get_quadrant_distribution(db: Session = Depends(get_db)) -> dict:
    quadrant_result = db.query(Task.quadrant, func.count(Task.id)).group_by(Task.quadrant).all()
    quadrant_stats = dict(quadrant_result)
    
    total = db.query(Task).count()
    
    percentages = {}
    for quadrant in ["Q1", "Q2", "Q3", "Q4"]:
        count = quadrant_stats.get(quadrant, 0)
        percentages[quadrant] = round((count / total) * 100, 2) if total > 0 else 0
    
    return {
        "absolute": quadrant_stats,
        "percentages": percentages,
        "total": total
    }

@router.get("/completion-timeline")
async def get_completion_timeline(db: Session = Depends(get_db)) -> dict:
    completed_tasks = db.query(Task).filter(Task.completed_at.isnot(None)).all()
    
    timeline = {}
    for task in completed_tasks:
        date_str = task.completed_at.strftime("%Y-%m-%d")
        if date_str not in timeline:
            timeline[date_str] = 0
        timeline[date_str] += 1
    
    return {
        "completion_timeline": timeline,
        "total_completed": len(completed_tasks)
    }

# НОВЫЙ ЭНДПОИНТ: Статистика по дедлайнам
@router.get("/deadlines")
async def get_deadline_stats(db: Session = Depends(get_db)) -> dict:
    today = date.today()
    
    # Распределение по статусам дедлайнов - ИСПРАВЛЕННЫЙ СИНТАКСИС
    deadline_status = db.query(
        func.count(Task.id).label('count'),
        case(
            (Task.deadline.is_(None), 'no_deadline'),
            (Task.deadline < today, 'overdue'),
            (Task.deadline == today, 'today'),
            (Task.deadline <= today + timedelta(days=3), 'within_3_days'),
            (Task.deadline <= today + timedelta(days=7), 'within_week'),
            (Task.deadline > today + timedelta(days=7), 'future'),
            else_='other'
        ).label('status')
    ).filter(Task.completed == False).group_by('status').all()
    
    status_dict = {status: count for count, status in deadline_status}
    
    # Ближайшие дедлайны
    upcoming_tasks = db.query(Task).filter(
        Task.deadline.isnot(None),
        Task.deadline >= today,
        Task.completed == False
    ).order_by(Task.deadline).limit(10).all()
    
    return {
        "deadline_distribution": status_dict,
        "upcoming_deadlines": [
            {
                "id": task.id,
                "title": task.title,
                "deadline": task.deadline,
                "days_until": task.calculate_days_until_deadline()
            }
            for task in upcoming_tasks
        ]
    }