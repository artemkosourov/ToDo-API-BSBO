from fastapi import APIRouter, HTTPException, Query, status, Depends
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete

from schemas import TaskCreate, TaskUpdate, TaskResponse
from database import get_db, calculate_quadrant
from models import Task

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"description": "Task not found"}},
)

@router.get("/", response_model=dict)
async def get_all_tasks(db: Session = Depends(get_db)) -> dict:
    tasks = db.query(Task).all()
    
    return {
        "count": len(tasks),
        "tasks": [task.to_dict() for task in tasks]
    }

@router.get("/search", response_model=dict)
async def search_tasks(
    q: str = Query(..., min_length=2, description="Ключевое слово для поиска"),
    db: Session = Depends(get_db)
) -> dict:
    search_term = f"%{q}%"
    
    filtered_tasks = db.query(Task).filter(
        (Task.title.ilike(search_term)) | 
        (Task.description.ilike(search_term))
    ).all()
    
    return {
        "query": q,
        "count": len(filtered_tasks),
        "tasks": [task.to_dict() for task in filtered_tasks]
    }

@router.get("/status/{status}", response_model=dict)
async def get_tasks_by_status(
    status: str, 
    db: Session = Depends(get_db)
) -> dict:
    if status not in ["completed", "pending"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Статус не найден. Используйте: 'completed' или 'pending'"
        )
    
    is_completed = status == "completed"
    filtered_tasks = db.query(Task).filter(Task.completed == is_completed).all()
    
    return {
        "status": status,
        "count": len(filtered_tasks),
        "tasks": [task.to_dict() for task in filtered_tasks]
    }

@router.get("/quadrant/{quadrant}", response_model=dict)
async def get_tasks_by_quadrant(
    quadrant: str, 
    db: Session = Depends(get_db)
) -> dict:
    if quadrant not in ["Q1", "Q2", "Q3", "Q4"]:
        raise HTTPException(
            status_code=400, 
            detail="Неверный квадрант. Используйте: Q1, Q2, Q3, Q4"
        )
    
    filtered_tasks = db.query(Task).filter(Task.quadrant == quadrant).all()
    
    return {
        "quadrant": quadrant,
        "count": len(filtered_tasks),
        "tasks": [task.to_dict() for task in filtered_tasks]
    }

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task_by_id(
    task_id: int, 
    db: Session = Depends(get_db)
) -> TaskResponse:
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Задача с ID {task_id} не найдена"
        )
    
    return task

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate, 
    db: Session = Depends(get_db)
) -> TaskResponse:
    quadrant = calculate_quadrant(task.is_important, task.is_urgent)
    
    new_task = Task(
        title=task.title,
        description=task.description,
        is_important=task.is_important,
        is_urgent=task.is_urgent,
        quadrant=quadrant,
        completed=False
    )
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    return new_task

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int, 
    task_update: TaskUpdate, 
    db: Session = Depends(get_db)
) -> TaskResponse:
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=404, 
            detail="Задача не найдена"
        )
    
    update_data = task_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(task, field, value)
    
    if "is_important" in update_data or "is_urgent" in update_data:
        task.quadrant = calculate_quadrant(
            task.is_important, 
            task.is_urgent
        )
    
    db.commit()
    db.refresh(task)
    
    return task

@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: int, 
    db: Session = Depends(get_db)
) -> TaskResponse:
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=404, 
            detail="Задача не найдена"
        )
    
    task.completed = True
    task.completed_at = datetime.now()
    
    db.commit()
    db.refresh(task)
    
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int, 
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=404, 
            detail="Задача не найдена"
        )
    
    db.delete(task)
    db.commit()
    
    return None