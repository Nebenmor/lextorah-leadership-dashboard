# backend/app/schemas.py
from typing import Literal

from pydantic import BaseModel


class ClassSummary(BaseModel):
    school_name: str
    class_name: str
    total_students: int
    avg_score: int
    avg_attendance: int
    declining_count: int
    low_attendance_count: int
    incomplete_practice_count: int
    at_risk_count: int


class StudentAnalysis(BaseModel):
    id: int
    name: str
    class_name: str
    attendance: int
    practice_completion: int
    speaking: int
    listening: int
    recent_scores: list[int]
    latest_score: int
    risk_score: int
    risk_level: Literal["high", "medium", "low"]
    flags: list[str]
    weak_skills: list[str]