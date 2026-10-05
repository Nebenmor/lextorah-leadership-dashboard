# backend/app/models.py

# backend/app/models.py
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    class_name: Mapped[str] = mapped_column(String(50))
    attendance: Mapped[int]
    practice_completion: Mapped[int]
    speaking: Mapped[int]
    listening: Mapped[int]
    recent_scores: Mapped[list[int]] = mapped_column(ARRAY(Integer))


class Insight(Base):
    """Cached AI insight, one per student."""

    __tablename__ = "insights"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), unique=True)
    payload: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )