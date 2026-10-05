# backend/tests/test_analytics.py
from types import SimpleNamespace

from app.analytics import (
    analyze_student,
    at_risk_students,
    class_summary,
    is_declining,
    rank_students,
)


def make_student(id=1, name="Test", attendance=90, practice=90, speaking=80,
                 listening=80, scores=(70, 72, 75)):
    return SimpleNamespace(
        id=id, name=name, class_name="French A1", attendance=attendance,
        practice_completion=practice, speaking=speaking, listening=listening,
        recent_scores=list(scores),
    )


def sarah():
    return make_student(
        id=1, name="Sarah", attendance=68, practice=20,
        speaking=38, listening=44, scores=(72, 64, 51),
    )


def test_is_declining():
    assert is_declining([72, 64, 51])
    assert not is_declining([60, 62, 61])
    assert not is_declining([60, 60, 55])
    assert not is_declining([60])


def test_sarah_is_high_risk_with_expected_flags():
    result = analyze_student(sarah())
    assert result["risk_level"] == "high"
    assert result["weak_skills"] == ["speaking", "listening"]
    assert len(result["flags"]) == 5


def test_healthy_student_is_low_risk():
    result = analyze_student(make_student())
    assert result["risk_level"] == "low"
    assert result["flags"] == []


def test_at_risk_sorted_highest_first_and_excludes_healthy():
    students = [make_student(id=2, name="Healthy"), sarah()]
    at_risk = at_risk_students(students)
    assert [a["name"] for a in at_risk] == ["Sarah"]
    assert [a["name"] for a in rank_students(students)] == ["Sarah", "Healthy"]


def test_class_summary_counts():
    students = [sarah(), make_student(id=2, name="A"), make_student(id=3, name="B")]
    summary = class_summary(students)
    assert summary["total_students"] == 3
    assert summary["declining_count"] == 1
    assert summary["low_attendance_count"] == 1
    assert summary["incomplete_practice_count"] == 1
    assert summary["at_risk_count"] == 1