from pydantic import BaseModel, Field, validator
from typing import Optional, Any, Dict
from datetime import datetime

class TaskBase(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Название задачи"
    )
    
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Описание задачи"
    )
    
    is_important: bool = Field(
        ...,
        description="Важность задачи"
    )
    
    is_urgent: bool = Field(
        ...,
        description="Срочность задачи"
    )
    
    @validator('title')
    def title_cannot_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Название задачи не может быть пустым')
        return v.strip()

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Новое название задачи"
    )
    
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Новое описание"
    )
    
    is_important: Optional[bool] = Field(
        None,
        description="Новая важность"
    )
    
    is_urgent: Optional[bool] = Field(
        None,
        description="Новая срочность"
    )
    
    completed: Optional[bool] = Field(
        None,
        description="Статус выполнения"
    )
    
    @validator('title')
    def title_cannot_be_empty(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Название задачи не может быть пустым')
        return v.strip() if v else v

class TaskResponse(TaskBase):
    id: int = Field(
        ...,
        description="Уникальный идентификатор задачи",
        examples=[1]
    )
    
    quadrant: str = Field(
        ...,
        description="Квадрант матрицы Эйзенхауэра (Q1, Q2, Q3, Q4)",
        examples=["Q1"]
    )
    
    completed: bool = Field(
        default=False,
        description="Статус выполнения задачи"
    )
    
    created_at: datetime = Field(
        ...,
        description="Дата и время создания задачи"
    )
    
    completed_at: Optional[datetime] = Field(
        None,
        description="Дата и время завершения задачи"
    )

    class Config:
        from_attributes = True