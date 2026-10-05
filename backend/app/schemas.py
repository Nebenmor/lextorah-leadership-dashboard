# backend/app/schemas.py
from typing import Literal

from pydantic import BaseModel, Field


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

class LLMInsight(BaseModel):
    """The only shape the LLM is allowed to return. Validated before use."""

    why: str = Field(min_length=10, max_length=500)
    primary_concern: str = Field(min_length=3, max_length=200)
    recommended_action: str = Field(min_length=10, max_length=500)


class InsightResponse(LLMInsight):
    """API response: computed facts from Python plus the interpretation."""

    student_id: int
    student_name: str
    risk_level: Literal["high", "medium", "low"]
    risk_score: int
    source: Literal["ai", "fallback"]
    cached: bool = False