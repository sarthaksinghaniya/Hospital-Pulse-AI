# How Hospital Pulse AI Works
Overview

Hospital Pulse AI is an AI-powered hospital operations decision-support platform that proactively forecasts Emergency Department (ER) load, ICU capacity pressure, and staff workload. It transforms raw operational signals into early warnings and actionable recommendations, enabling hospital administrators to prepare before overload occurs, not after.

# Data

Synthetic, hourly operational data (default: last 90 days) simulates realistic hospital activity:

ER admissions and ambulance arrivals

ICU occupancy and discharge rates

Staffing levels and handling time

Flu cases, surgical volume, weather, and seasonality indicators

Data is auto-generated on first backend startup and regenerated if the dataset is incomplete or too short.

No patient-level or identifiable information is used — all data is aggregated, anonymized, and privacy-safe by design.

# Modeling Approach

Hospital Pulse AI prioritizes interpretability and reliability over black-box complexity.

Linear regression baselines for ER and ICU demand using time, trend, and seasonal features.

Lightweight temporal smoothing (LSTM-inspired) to capture short-term momentum without heavy deep-learning dependencies.

Rule-based surge and staffing risk engines to ensure explainable alerts and recommendations.

Optional OpenAI LLM integration for natural-language summaries when OPENAI_API_KEY is available; robust rule-based fallbacks ensure full functionality without it.

# Core Predictions

Emergency Load Forecast

Hourly ER demand for the next 7 days

Surge probability and threshold tracking

ICU Capacity Monitor

Projected ICU occupancy

Peak risk vs fixed 40-bed capacity

Capacity pressure visualization

Staff Workload Heatmap

Shift-wise nurse-to-patient stress scores

Early identification of high-risk shifts

Alerts & Recommendations

# Alerts

Severity-based warnings (Critical / Caution / Info)

Time-windowed predictions (~48h) for the next 72 hours

Designed to enable early operational response

# AI Recommendations

Actionable, rule-driven steps (staffing, ICU prep, communication)

Priority tags (High / Medium)

Clear “Why this matters” explanations for every recommendation

SEWI (Surge Early-Warning Index)

Composite operational risk score combining ER, ICU, and staff stress

Transparent drivers and recommended actions

See FEATURE_SEWI.md for full methodology

# UI / UX Design

Hospital-grade visual language with calm medical blues and high-contrast indicators.

Information hierarchy optimized for decision-making:

SEWI / Readiness Score

Alerts

ER Forecast

ICU Capacity

Staff Workload

AI Recommendations

Skeleton loaders for data fetch, subtle animations, and hover cues for interactivity.

Trust indicators:

Aggregated Data

Interpretable AI

Decision Support Only

HOPX Chat Assistant

Embedded bottom-right AI assistant with welcome message and quick-question chips.

Answers operational questions related to:

SEWI and readiness

Alerts and recommendations

ICU, staff, and ER forecasts

Powered by backend rule-based logic; optionally enhanced by OpenAI.

Smart auto-scroll and visibility-aware positioning for seamless UX.

# API Endpoints

POST /predict/emergency – ER forecast, surge probability, summary

POST /predict/icu – ICU forecast, peak risk, summary

POST /predict/staff – Staff workload risk, summary

GET /alerts – Alerts list with explanation

GET /recommendations – Actionable recommendations

GET /feature/surge-early-warning – SEWI score and drivers

POST /feature/hopx-chat – HOPX assistant Q&A

GET /health – Service health check

Run Locally
Backend (FastAPI)
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Optional: set OPENAI_API_KEY in backend/env/.env
python -m uvicorn backend.main:app --reload --port 8000

Frontend (React + Vite)
cd frontend
npm install
npm run dev -- --host --port 5173

Ethical & Safety Safeguards

No patient-level or identifiable data.

All outputs are decision support, not clinical directives.

Explicit UI disclaimers and interpretability labels.

Graceful fallback behavior if LLM services are unavailable.

Tech Stack

Backend: Python, FastAPI, pandas, NumPy, scikit-learn, optional OpenAI

Frontend: React, Vite, Material-UI, Recharts, Axios

Data: Synthetic CSV generation on demand