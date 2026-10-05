# backend/tests/test_insights.py
from types import SimpleNamespace

import pytest

from app import insights
from app.analytics import analyze_student, class_summary

SUMMARY = {"avg_score": 62, "avg_attendance": 74, "total_students": 30}
VALID = (
    '{"why": "Scores fell from 72% to 51% with low attendance.",'
    ' "primary_concern": "Speaking and listening",'
    ' "recommended_action": "Assign targeted speaking practice and alert the tutor."}'
)


@pytest.fixture
def sarah():
    return analyze_student(
        SimpleNamespace(
            id=1, name="Sarah", class_name="French A1", attendance=68,
            practice_completion=20, speaking=38, listening=44,
            recent_scores=[72, 64, 51],
        )
    )


def test_facts_contain_computed_values_only(sarah):
    facts = insights.build_facts(sarah, SUMMARY)
    assert facts["student"]["risk_level"] == "high"
    assert facts["student"]["weak_skills"] == ["speaking", "listening"]
    assert "id" not in facts["student"]


def test_fallback_when_no_api_key(sarah, monkeypatch):
    monkeypatch.setattr(insights.settings, "groq_api_key", "")
    insight, source = insights.generate_insight(sarah, SUMMARY)
    assert source == "fallback"
    assert "speaking and listening" in insight.recommended_action


def test_ai_path_validates_output(sarah, monkeypatch):
    monkeypatch.setattr(insights.settings, "groq_api_key", "key")
    monkeypatch.setattr(insights, "_call_groq", lambda facts: VALID)
    insight, source = insights.generate_insight(sarah, SUMMARY)
    assert source == "ai"
    assert insight.primary_concern == "Speaking and listening"


def test_retries_once_on_invalid_json(sarah, monkeypatch):
    monkeypatch.setattr(insights.settings, "groq_api_key", "key")
    replies = iter(["not json", VALID])
    monkeypatch.setattr(insights, "_call_groq", lambda facts: next(replies))
    _, source = insights.generate_insight(sarah, SUMMARY)
    assert source == "ai"


def test_falls_back_after_repeated_failures(sarah, monkeypatch):
    monkeypatch.setattr(insights.settings, "groq_api_key", "key")

    def boom(facts):
        raise RuntimeError("groq down")

    monkeypatch.setattr(insights, "_call_groq", boom)
    _, source = insights.generate_insight(sarah, SUMMARY)
    assert source == "fallback"