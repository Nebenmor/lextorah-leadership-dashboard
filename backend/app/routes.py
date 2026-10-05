# backend/app/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.analytics import analyze_student, at_risk_students, class_summary
from app.database import get_db
from app.insights import generate_insight
from app.models import Insight, Student
from app.schemas import ClassSummary, InsightResponse, StudentAnalysis

router = APIRouter(prefix="/api")

SCHOOL_NAME = "Lextorah Demo School"


def _all_students(db: Session) -> list[Student]:
    students = list(db.scalars(select(Student).order_by(Student.id)))
    if not students:
        raise HTTPException(status_code=404, detail="No data found. Run seed.py first.")
    return students


@router.get("/class/summary", response_model=ClassSummary)
def get_class_summary(db: Session = Depends(get_db)):
    students = _all_students(db)
    return {
        "school_name": SCHOOL_NAME,
        "class_name": students[0].class_name,
        **class_summary(students),
    }


# NOTE: /students/at-risk must be declared before /students/{student_id}
@router.get("/students/at-risk", response_model=list[StudentAnalysis])
def get_at_risk_students(db: Session = Depends(get_db)):
    return at_risk_students(_all_students(db))


@router.get("/students/{student_id}", response_model=StudentAnalysis)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return analyze_student(student)

@router.post("/students/{student_id}/insight", response_model=InsightResponse)
def create_student_insight(
    student_id: int, refresh: bool = False, db: Session = Depends(get_db)
):
    """AI interpretation of one student's computed facts. AI results are cached."""
    students = _all_students(db)
    student = next((s for s in students if s.id == student_id), None)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    analysis = analyze_student(student)
    base = {
        "student_id": student.id,
        "student_name": analysis["name"],
        "risk_level": analysis["risk_level"],
        "risk_score": analysis["risk_score"],
    }

    cached = db.scalar(select(Insight).where(Insight.student_id == student_id))
    if cached and not refresh:
        return {**base, **cached.payload, "source": "ai", "cached": True}

    insight, source = generate_insight(analysis, class_summary(students))
    payload = insight.model_dump()

    # Only AI output is cached, so a fallback never blocks a later AI attempt.
    if source == "ai":
        if cached:
            cached.payload = payload
            cached.created_at = func.now()
        else:
            db.add(Insight(student_id=student_id, payload=payload))
        db.commit()

    return {**base, **payload, "source": source, "cached": False}