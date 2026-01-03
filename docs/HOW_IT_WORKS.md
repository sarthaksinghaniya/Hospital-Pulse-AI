# How Hospital Pulse AI Works

## Overview
Hospital Pulse AI is a decision-support tool that forecasts Emergency Department load, ICU demand, and staff workload, then surfaces alerts and actionable recommendations to help administrators prepare before overload occurs.

## Data
- **Synthetic hourly data** (90 days by default) includes ER admissions, ICU occupancy, staffing levels, handling time, weather/seasonality signals, and realistic clinical fields (ambulance arrivals, flu cases, surgical cases, discharge rate).
- Auto-generated on first backend start if missing; regenerated if the file is too short.
- No patient identifiers; purely aggregated and anonymized.

## Models
- **Linear regression baselines** for ER and ICU forecasts using time/seasonal features.
- **Lightweight LSTM-like smoother** to add temporal decay without deep learning complexity.
- **Rule-based surge/staff risk estimators** for interpretable alerts and recommendations.
- **Optional OpenAI LLM** to polish text summaries when OPENAI_API_KEY is set; otherwise safe fallbacks.

## Predictions
- **Emergency Load Forecast**: Hourly ER admissions for the next 7 days with surge probability.
- **ICU Capacity Monitor**: Projected ICU beds needed and peak risk vs 40-bed capacity.
- **Staff Workload Heatmap**: Shift-by-shift nurse-to-patient stress scores.

## Alerts & Recommendations
- **Alerts**: Early warnings (Critical/Caution/Info) with time windows (~48h) for next 72 hours.
- **Recommendations**: Actionable, rule-based actions with priority tags and “Why this matters” rationale.
- **SEWI**: Composite operational risk score (see FEATURE_SEWI.md).

## UI/UX
- Hospital-grade, calm design with medical blue palette.
- Priority order: SEWI/Readiness → Alerts → ER Forecast → ICU → Staff → Recommendations.
- Skeleton loaders during data fetch; subtle hover and transitions.
- Trust badges: Aggregated Data, Interpretable AI, Decision Support Only.

## Chat Assistant (HOPX)
- Mini chat bot in the bottom-right with welcome message and quick-question chips.
- Answers questions about SEWI, alerts, recommendations, ICU, staff, forecasts, and readiness.
- Uses backend rule-based replies; optionally enhanced by OpenAI if available.
- Auto-scrolls to latest messages and scrolls the page just enough to keep chat visible.

## API endpoints
- `POST /predict/emergency` – ER forecast + surge probability + summary
- `POST /predict/icu` – ICU forecast + peak risk + summary
- `POST /predict/staff` – Staff workload risk + summary
- `GET /alerts` – Alert list + summary
- `GET /recommendations` – Recommendations + summary
- `GET /feature/surge-early-warning` – SEWI composite score and actions
- `POST /feature/hopx-chat` – HOPX assistant Q&A
- `GET /health` – Service status

## Run locally
1) Backend (FastAPI)
   ```bash
   cd backend
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   # Set OPENAI_API_KEY in backend/env/.env if desired
   python -m uvicorn backend.main:app --reload --port 8000
   ```

2) Frontend (React/Vite)
   ```bash
   cd frontend
   npm install
   npm run dev -- --host --port 5173
   ```

## Ethical safeguards
- No patient-level data.
- All outputs are decision support, not medical decisions.
- Clear UI disclaimers and “Interpretable AI” tags.
- Fallback behavior when LLM is unavailable.

## Tech stack
- Backend: Python, FastAPI, pandas/numpy, scikit-learn, optional OpenAI
- Frontend: React, Vite, Material-UI, Recharts, Axios
- Data: CSV (synthetic), generated on demand.
