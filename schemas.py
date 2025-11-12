from pydantic import BaseModel, Field, validator
from typing import Optional, Any, Dict
from datetime import datetime, date

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
    
    # НОВОЕ ПОЛЕ: Дедлайн задачи
    deadline: Optional[date] = Field(
        None,
        description="Дедлайн задачи (YYYY-MM-DD)"
    )
    
    @validator('title')
    def title_cannot_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Название задачи не может быть пустым')
        return v.strip()
    
    @validator('deadline')
    def deadline_cannot_be_in_past(cls, v):
        if v and v < date.today():
            raise ValueError('Дедлайн не может быть в прошлом')
        return v

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
    
    # НОВОЕ ПОЛЕ: Дедлайн задачи
    deadline: Optional[date] = Field(
        None,
        description="Дедлайн задачи (YYYY-MM-DD)"
    )
    
    @validator('title')
    def title_cannot_be_empty(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Название задачи не может быть пустым')
        return v.strip() if v else v
    
    @validator('deadline')
    def deadline_cannot_be_in_past(cls, v):
        if v and v < date.today():
            raise ValueError('Дедлайн не может быть в прошлом')
        return v

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
    
    # Новые вычисляемые поля для ответа
    days_until_deadline: Optional[int] = Field(
        None,
        description="Количество дней до дедлайна"
    )
    
    is_overdue: bool = Field(
        default=False,
        description="Просрочена ли задача"
    )

    class Config:
        from_attributes = True