from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import predictions, alerts, recommendations, feature, vitals, adherence, noshow, deterioration_risk, escalation
from services.synthetic_data import ensure_synthetic_dataset
from services.model_service import ModelService
from services.model_registry import set_model_service

ENV_PATH = Path(__file__).resolve().parents[1] / "env" / ".env"
load_dotenv(ENV_PATH)

app = FastAPI(title="Hospital Pulse AI", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model_service: ModelService | None = None


@app.on_event("startup")
async def startup_event():
    ensure_synthetic_dataset()
    service = ModelService()
    set_model_service(service)


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(predictions.router, prefix="/predict", tags=["predictions"], dependencies=[])
app.include_router(alerts.router, prefix="/alerts", tags=["alerts"], dependencies=[])
app.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"], dependencies=[])
app.include_router(feature.router, prefix="/feature", tags=["feature"], dependencies=[])
app.include_router(vitals.router, prefix="/vitals", tags=["vitals"], dependencies=[])
app.include_router(adherence.router, prefix="/adherence", tags=["adherence"], dependencies=[])
app.include_router(noshow.router, prefix="/noshow", tags=["noshow"], dependencies=[])
app.include_router(deterioration_risk.router, prefix="/risk", tags=["risk"], dependencies=[])
app.include_router(escalation.router, prefix="/escalation", tags=["escalation"], dependencies=[])


@app.get("/")
def root():
    return {
        "message": "Hospital Pulse AI - decision support tool",
        "endpoints": [
            "/health",
            "/predict/emergency",
            "/predict/icu",
            "/predict/staff",
            "/alerts",
            "/recommendations",
            "/vitals/overview",
            "/vitals/patient-summary",
            "/adherence/population-overview",
            "/adherence/score",
            "/noshow/train",
            "/noshow/predict",
            "/risk/assess",
            "/escalation/dashboard",
        ],
    }
