# backend/app/insights.py
"""AI interpretation layer. The LLM explains pre-computed facts; it never computes them.

Flow: analytics facts -> prompt -> Groq -> Pydantic validation -> (retry once) -> fallback.
"""
import json
import logging

from groq import Groq

from app.config import settings
from app.schemas import LLMInsight

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 2

SYSTEM_PROMPT = """You are an education analyst assisting a school leader.
You receive pre-computed facts about one student as JSON. All numbers and risk levels
were computed by software. Do not recalculate them or contradict them.

Rules:
- Use only the facts provided. Never invent causes, personal circumstances, diagnoses or numbers.
- "why": 1 to 2 sentences explaining what is happening. Cite the most important figures and,
  where useful, compare the student with the class averages.
- "primary_concern": a short phrase naming the main problem area (for example the weakest skill).
- "recommended_action": 1 to 2 concrete steps a school leader can take now, such as assigning
  targeted practice for a weak skill, alerting the tutor, or contacting the guardian about
  attendance. Name the skill when relevant.
- Plain, professional tone. No markdown.

Respond with a JSON object with exactly these keys: why, primary_concern, recommended_action."""

STUDENT_FIELDS = (
    "name",
    "class_name",
    "risk_level",
    "risk_score",
    "attendance",
    "practice_completion",
    "speaking",
    "listening",
    "recent_scores",
    "flags",
    "weak_skills",
)


def build_facts(analysis: dict, summary: dict) -> dict:
    """The only data the LLM sees: computed facts, no raw database rows."""
    return {
        "student": {k: analysis[k] for k in STUDENT_FIELDS},
        "scores_order": "oldest to newest, percent",
        "class_averages": {
            "avg_score": summary["avg_score"],
            "avg_attendance": summary["avg_attendance"],
            "total_students": summary["total_students"],
        },
    }


def _call_groq(facts: dict) -> str:
    client = Groq(api_key=settings.groq_api_key, timeout=15.0, max_retries=0)
    response = client.chat.completions.create(
        model=settings.groq_model,
        temperature=0.2,
        reasoning_effort="low",  # gpt-oss models reason first; keep it short and cheap
        max_completion_tokens=1500,  # reasoning tokens count toward this limit
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "Facts:\n" + json.dumps(facts)},
        ],
    )
    return response.choices[0].message.content or ""


def _join(items: list[str]) -> str:
    if len(items) <= 2:
        return " and ".join(items)
    return ", ".join(items[:-1]) + ", and " + items[-1]


def fallback_insight(analysis: dict) -> LLMInsight:
    """Rule-based insight used when the LLM is unavailable or returns invalid output."""
    name = analysis["name"]
    flags = analysis["flags"]
    skills = analysis["weak_skills"]

    if flags:
        why = f"{name} is flagged for: " + "; ".join(f.lower() for f in flags) + "."
    else:
        why = f"{name} shows no significant risk indicators at the moment."

    if skills:
        concern = "Weak " + " and ".join(skills)
    elif flags:
        concern = flags[0].split(" (")[0]
    else:
        concern = "No major concern"

    steps = []
    if skills:
        steps.append(f"assign targeted {' and '.join(skills)} practice")
    elif analysis["practice_completion"] < 50:
        steps.append("follow up on the recommended practice")
    if analysis["attendance"] < 75:
        steps.append("contact the guardian about attendance")
    steps.append("alert the tutor for follow-up")
    action = _join(steps)
    action = action[0].upper() + action[1:] + "."

    return LLMInsight(why=why, primary_concern=concern, recommended_action=action)


def generate_insight(analysis: dict, summary: dict) -> tuple[LLMInsight, str]:
    """Returns (insight, source) where source is "ai" or "fallback"."""
    if settings.groq_api_key:
        facts = build_facts(analysis, summary)
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                return LLMInsight.model_validate_json(_call_groq(facts)), "ai"
            except Exception as exc:  # validation error, API error, timeout
                logger.warning("Insight attempt %d failed: %s", attempt, exc)
    return fallback_insight(analysis), "fallback"