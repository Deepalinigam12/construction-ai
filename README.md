# Multimodal Construction Intelligence Platform

React + FastAPI app that analyses construction photos and text with a multimodal LLM (Claude).

| Feature | Endpoint | Notes |
|---|---|---|
| Site safety and PPE check | `POST /api/safety/analyze` | image + notes, strict JSON |
| Crack type, severity, causes, actions | `POST /api/cracks/analyze` | image + notes, strict JSON |
| Material estimate, cost, schedule | `POST /api/planning/estimate` | deterministic engine (INR) + AI notes |
| Real-estate valuation | `POST /api/valuation/estimate` | rule-based range + AI summary |
| Weather advisory (go / caution / no-go) | `GET /api/weather?city=` | Open-Meteo, no key needed |
| Construction knowledge assistant | `POST /api/assistant/chat` | chat with history |
| Health | `GET /api/health` | shows whether AI is enabled |

Every AI response is validated against a Pydantic schema (`backend/app/schemas.py`). If the model output is malformed it is retried once, then falls back to a safe response, so the UI never breaks.
Without `ANTHROPIC_API_KEY` the app runs in **demo mode**: planning, valuation, weather and chat keywords work; image analysis returns a clearly labelled sample.

## Run it

Requires Python 3.9+ and Node.js 18+.

```bash
# Terminal 1: backend
cd backend
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                  # then add ANTHROPIC_API_KEY
uvicorn app.main:app --reload --port 8000

# Terminal 2: frontend
cd frontend
npm install
npm run dev                                           # http://localhost:5173
```

API docs: http://localhost:8000/docs. Tests: `cd backend && pytest`.

## Project layout

```
backend/app/   main.py (routes) llm.py (LLM + JSON validation) schemas.py planning.py demo.py weather.py
backend/tests/ test_api.py
frontend/src/  App.jsx api.js pages/ components/ styles.css
```

## Known limitations

- AI image analysis is advisory; cracks and safety findings need a qualified engineer's confirmation.
- Cost and valuation rates are generic Indian averages; override with local rates.
- The weather tab needs internet access.
- Uploaded images are sent to the AI API and not stored.
