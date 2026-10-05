# backend/app/analytics.py
"""Deterministic analytics and risk scoring. No AI in this file.

Works with any object exposing the Student fields (ORM model or plain object).
"""

# Thresholds (kept in sync with the metric definitions in seed.py)
LOW_ATTENDANCE = 75
LOW_PRACTICE = 50
WEAK_SKILL = 50
AT_RISK_THRESHOLD = 30  # risk_score at or above this counts as "at risk"
HIGH_RISK_THRESHOLD = 60


def is_declining(scores: list[int]) -> bool:
    """True if every score is lower than the one before it."""
    return len(scores) >= 2 and all(a > b for a, b in zip(scores, scores[1:]))


def _severity(value: float, ok: float, worst: float) -> float:
    """0.0 at the 'ok' value, 1.0 at the 'worst' value, linear in between."""
    ratio = (value - ok) / (worst - ok)
    return max(0.0, min(1.0, ratio))


def analyze_student(student) -> dict:
    scores = list(student.recent_scores)
    drop = scores[0] - scores[-1]
    min_skill = min(student.speaking, student.listening)

    # Risk score (0-100): trend 30, attendance 25, practice 25, skills 20
    risk = (
        30 * _severity(drop, ok=0, worst=20)
        + 25 * _severity(student.attendance, ok=LOW_ATTENDANCE, worst=60)
        + 25 * _severity(student.practice_completion, ok=LOW_PRACTICE, worst=10)
        + 20 * _severity(min_skill, ok=60, worst=30)
    )
    risk_score = round(risk)

    flags = []
    if is_declining(scores):
        flags.append("Declining scores (" + " → ".join(f"{s}%" for s in scores) + ")")
    if student.attendance < LOW_ATTENDANCE:
        flags.append(f"Low attendance ({student.attendance}%)")
    if student.practice_completion < LOW_PRACTICE:
        flags.append(f"Low practice completion ({student.practice_completion}%)")

    weak_skills = []
    if student.speaking < WEAK_SKILL:
        weak_skills.append("speaking")
        flags.append(f"Weak speaking ({student.speaking}%)")
    if student.listening < WEAK_SKILL:
        weak_skills.append("listening")
        flags.append(f"Weak listening ({student.listening}%)")

    if risk_score >= HIGH_RISK_THRESHOLD:
        level = "high"
    elif risk_score >= AT_RISK_THRESHOLD:
        level = "medium"
    else:
        level = "low"

    return {
        "id": student.id,
        "name": student.name,
        "class_name": student.class_name,
        "attendance": student.attendance,
        "practice_completion": student.practice_completion,
        "speaking": student.speaking,
        "listening": student.listening,
        "recent_scores": scores,
        "latest_score": scores[-1],
        "risk_score": risk_score,
        "risk_level": level,
        "flags": flags,
        "weak_skills": weak_skills,
    }


def rank_students(students) -> list[dict]:
    """All students analyzed, highest risk first."""
    analyzed = [analyze_student(s) for s in students]
    return sorted(analyzed, key=lambda a: (-a["risk_score"], a["latest_score"]))


def at_risk_students(students) -> list[dict]:
    return [a for a in rank_students(students) if a["risk_score"] >= AT_RISK_THRESHOLD]


def class_summary(students) -> dict:
    students = list(students)
    n = len(students)
    return {
        "total_students": n,
        "avg_score": round(sum(s.recent_scores[-1] for s in students) / n),
        "avg_attendance": round(sum(s.attendance for s in students) / n),
        "declining_count": sum(1 for s in students if is_declining(list(s.recent_scores))),
        "low_attendance_count": sum(1 for s in students if s.attendance < LOW_ATTENDANCE),
        "incomplete_practice_count": sum(
            1 for s in students if s.practice_completion < LOW_PRACTICE
        ),
        "at_risk_count": len(at_risk_students(students)),
    }