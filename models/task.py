from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Date
from sqlalchemy.sql import func
from database import Base
from datetime import date
from typing import Optional
class Task(Base):
    __tablename__ = "tasks"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )
    
    title = Column(
        Text,
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    is_important = Column(
        Boolean,
        nullable=False,
        default=False
    )

    is_urgent = Column(
        Boolean,
        nullable=False,
        default=False
    )

    quadrant = Column(
        String(2),
        nullable=False
    )

    completed = Column(
        Boolean,
        nullable=False,
        default=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    # НОВОЕ ПОЛЕ: Дедлайн задачи
    deadline = Column(
        Date,
        nullable=True
    )

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title='{self.title}', quadrant='{self.quadrant}')>"

    def to_dict(self) -> dict:
        # Добавляем расчет дней до дедлайна
        days_until_deadline = self.calculate_days_until_deadline()
        
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "is_important": self.is_important,
            "is_urgent": self.is_urgent,
            "quadrant": self.quadrant,
            "completed": self.completed,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "deadline": self.deadline,
            "days_until_deadline": days_until_deadline,
            "is_overdue": days_until_deadline is not None and days_until_deadline < 0
        }

    def calculate_days_until_deadline(self) -> Optional[int]:
        """Рассчитывает количество дней до дедлайна"""
        if not self.deadline:
            return None
        
        today = date.today()
        delta = self.deadline - today
        return delta.days