# backend/app/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analytics import analyze_student, at_risk_students, class_summary
from app.database import get_db
from app.models import Student
from app.schemas import ClassSummary, StudentAnalysis

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