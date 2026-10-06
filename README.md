# Lextorah Leadership Dashboard

An AI-powered dashboard that helps school leaders see how a class is performing, identify students who need attention, and get a clear explanation with a recommended action.

**Live demo:** https://lextorah-leadership-dashboard.vercel.app

**API docs:** https://leadership-api-k0yk.onrender.com/docs

> The API runs on a free hosting tier and sleeps when idle. The first load can take up to a minute; the UI shows a loading state and retries automatically.

## Features
- **Class overview:** average score, average attendance, declining scores, low attendance, incomplete practice and students at risk.
- **At-risk ranking:** students ordered by a transparent 0-100 risk score, with the exact flags that triggered it.
- **Student detail:** key metrics and a recent-score trend chart.
- **AI insight:** an explanation of *why* a student is struggling, the *primary concern* and a *recommended action*.

## Architecture
![Architecture diagram](docs/architecture.png)

**Python decides, the LLM explains.**
- `analytics.py` computes every number and risk level with deterministic, unit-tested rules. No AI is involved.
- `insights.py` sends the LLM only the pre-computed facts. The model never sees raw database rows and never does arithmetic.
- LLM output is requested as JSON, validated with **Pydantic v2**, retried once on failure, and replaced by a **rule-based fallback** if the model is unavailable. Every response reports `source: "ai" | "fallback"`.
- Only AI output is cached (one row per student), so a fallback never blocks a later AI attempt. Use `?refresh=true` to regenerate.

## Tech Stack
| Layer | Technology |
|---|---|
| Frontend | React 19, TypeScript, Vite, Tailwind CSS 4, Recharts |
| Backend | Python 3.12, FastAPI, SQLAlchemy 2, Pydantic v2, pydantic-settings |
| Database | PostgreSQL (psycopg 3) |
| AI | Groq API, `openai/gpt-oss-120b` (JSON mode, low temperature) |
| Testing | pytest |
| Hosting | Vercel (frontend), Render (API), Neon (Postgres) |

## Project Structure
```
lextorah-leadership-dashboard/
├── README.md
├── render.yaml                  # Render blueprint for the API service
├── docs/
│   ├── architecture.png         # Architecture diagram
│   ├── architecture.svg
│   └── demo-script.md           # Walkthrough script for the demo
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   ├── seed.py                  # Creates tables and loads 30 mock students
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS, /health
│   │   ├── config.py            # Environment settings
│   │   ├── database.py          # SQLAlchemy engine and session
│   │   ├── models.py            # Database models (students, insights)
│   │   ├── schemas.py           # Pydantic v2 models (API and LLM output)
│   │   ├── routes.py            # REST endpoints
│   │   ├── analytics.py         # KPIs, flags and risk score (NO AI)
│   │   └── insights.py          # Prompt, validation, fallback (AI ONLY)
│   └── tests/
│       ├── conftest.py
│       ├── test_analytics.py
│       └── test_insights.py
└── frontend/
    ├── package.json
    ├── vercel.json
    ├── vite.config.ts
    ├── .env.example
    └── src/
        ├── main.tsx
        ├── App.tsx              # Page state and layout
        ├── api.ts               # API client with retry for cold starts
        ├── types.ts
        ├── risk.ts              # Risk badge styles
        └── components/
            ├── SummaryCards.tsx
            ├── AtRiskTable.tsx
            ├── StudentPanel.tsx
            ├── InsightCard.tsx
            └── LoadingSkeleton.tsx
```

## How the risk score works
A student's score (0-100) is the sum of four weighted signals, all defined in `analytics.py`:

| Signal | Weight | Triggered when |
|---|---|---|
| Declining scores | 30 | Recent scores trend downward |
| Low attendance | 25 | Attendance below 75% |
| Low practice completion | 25 | Practice completion below 50% |
| Weak speaking or listening | 20 | Either skill below 50% |

A score of 30 or more marks a student as **at risk**; 60 or more is **high risk**. All thresholds are named constants in one file.

## API Reference
| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/api/class/summary` | Class-level KPIs |
| GET | `/api/students/at-risk` | At-risk students, ranked, with flags |
| GET | `/api/students/{id}` | Analysis for one student |
| POST | `/api/students/{id}/insight` | AI insight (cached); add `?refresh=true` to regenerate |

Interactive documentation is available at `/docs`.

## Getting Started

### Prerequisites
Python 3.12, Node.js 20+ and PostgreSQL. A quick local database with Docker:
```bash
docker run --name leadership-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=leadership -p 5432:5432 -d postgres:16
```

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then add your GROQ_API_KEY
python seed.py                   # drops and recreates tables, loads 30 students
uvicorn app.main:app --reload    # http://localhost:8000
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env
npm run dev                      # http://localhost:5173
```

### Tests
```bash
cd backend
pytest
```

### Environment variables
| Variable | Where | Description |
|---|---|---|
| `DATABASE_URL` | Backend | Postgres connection string (`postgresql://` is converted to the psycopg 3 driver automatically) |
| `GROQ_API_KEY` | Backend | Groq API key. If empty, the rule-based fallback is used |
| `GROQ_MODEL` | Backend | Defaults to `openai/gpt-oss-120b` |
| `FRONTEND_URL` | Backend | Allowed CORS origin, e.g. `https://your-app.vercel.app` (no trailing slash) |
| `VITE_API_URL` | Frontend | Base URL of the API (no trailing slash). Read at build time |

## Deployment
1. **Database:** create a Postgres database on Neon and copy the connection string (keep `?sslmode=require`).
2. **Seed once** from your machine: `DATABASE_URL="<neon-url>" python seed.py` (PowerShell: `$env:DATABASE_URL='<neon-url>'`).
3. **API:** connect the repo to Render as a Blueprint (`render.yaml`), then set `DATABASE_URL`, `GROQ_API_KEY` and `FRONTEND_URL` in the dashboard.
4. **Frontend:** import the repo into Vercel with the root directory set to `frontend` and add `VITE_API_URL`. Redeploy after changing it.

## Design Decisions
- **Separation of logic and AI** makes results reproducible and auditable, and keeps AI failures from affecting the dashboard.
- **Graceful degradation:** validation, one retry and a deterministic fallback mean a usable insight is always returned.
- **Resilient client:** capped exponential backoff within a time budget plus an instant loading skeleton handle free-tier cold starts.
- **Intentionally simple:** one service, four endpoints, no auth, and `seed.py` instead of a migration tool, to keep the prototype focused.

## Author
Anthony Nebenmor, built as a technical assessment for Lextorah.