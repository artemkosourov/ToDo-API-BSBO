from fastapi import APIRouter
from database import tasks_db

router = APIRouter(
    prefix="/stats",
    tags=["statistics"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def get_tasks_stats() -> dict:
    total_tasks = len(tasks_db)
    
    by_quadrant = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}
    for task in tasks_db:
        quadrant = task["quadrant"]
        if quadrant in by_quadrant:
            by_quadrant[quadrant] += 1
    
    completed = sum(1 for task in tasks_db if task["completed"])
    pending = total_tasks - completed
    
    important_tasks = sum(1 for task in tasks_db if task["is_important"])
    urgent_tasks = sum(1 for task in tasks_db if task["is_urgent"])
    
    completed_with_date = sum(1 for task in tasks_db if task["completed_at"] is not None)
    
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
        }
    }

@router.get("/quadrant-distribution")
async def get_quadrant_distribution() -> dict:
    quadrant_stats = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}
    
    for task in tasks_db:
        quadrant = task["quadrant"]
        if quadrant in quadrant_stats:
            quadrant_stats[quadrant] += 1
    
    total = len(tasks_db)
    percentages = {}
    for quadrant, count in quadrant_stats.items():
        percentages[quadrant] = round((count / total) * 100, 2) if total > 0 else 0
    
    return {
        "absolute": quadrant_stats,
        "percentages": percentages,
        "total": total
    }

@router.get("/completion-timeline")
async def get_completion_timeline() -> dict:
    completed_tasks = [task for task in tasks_db if task["completed_at"] is not None]
    
    timeline = {}
    for task in completed_tasks:
        date_str = task["completed_at"].strftime("%Y-%m-%d")
        if date_str not in timeline:
            timeline[date_str] = 0
        timeline[date_str] += 1
    
    return {
        "completion_timeline": timeline,
        "total_completed": len(completed_tasks)
    }