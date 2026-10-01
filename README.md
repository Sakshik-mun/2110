# Credit Assistant

AI-powered credit health platform for the Indian CIBIL (300–900) ecosystem.
**Stack:** FastAPI · SQLAlchemy · SQLite · React (Vite) · Recharts · Google Gemini.

## Features
- Register / login (PBKDF2 password hashing, JWT sessions, protected routes, logout)
- Financial profile with validation
- Score history, DTI, utilization, savings rate, health score, risk detection
- Gemini-powered analysis and chat (rule-based fallback when no API key is set)
- Dashboard: score history line chart, utilization pie chart, risks, latest AI recommendation

## Setup
```bash
cp .env.example backend/.env      # add GEMINI_API_KEY and a strong SECRET_KEY

# Backend
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000               # docs: http://localhost:8000/docs

# Frontend (new terminal)
cd frontend
npm install
npm run dev                                         # http://localhost:5173
```

## Tests
```bash
cd backend && pytest -q
```

## API
| Method | Path | Purpose |
|---|---|---|
| POST | /api/auth/register, /api/auth/login | Get access token |
| GET | /api/auth/me | Current user |
| POST | /api/auth/logout | Logout (client discards token) |
| GET/PUT | /api/profile | Financial profile |
| GET/POST | /api/scores | Score history / add score |
| GET | /api/dashboard | Metrics, chart data, latest advice |
| POST | /api/advisor/analyze | Full AI analysis |
| POST | /api/advisor/chat | Ask the AI advisor |
| GET | /api/recommendations | Saved recommendations |

## Notes
- Guidance is informational, not licensed financial advice.
- The token is kept in `localStorage` for simplicity; use httpOnly cookies for production.
- Never commit `.env`.
