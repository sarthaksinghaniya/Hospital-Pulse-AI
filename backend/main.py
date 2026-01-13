from pathlib import Path
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import predictions, alerts, recommendations, feature, vitals, adherence, noshow, deterioration_risk, escalation, chatbot
from services.synthetic_data import ensure_synthetic_dataset
from services.model_service import ModelService
from services.model_registry import set_model_service

ENV_PATH = Path(__file__).resolve().parents[1] / "env" / ".env"
load_dotenv(ENV_PATH)

app = FastAPI(title="Hospital Pulse AI", version="0.1.0")

# Configure CORS for development and production
def get_cors_origins():
    """Get allowed origins based on environment"""
    origins = [
        "http://localhost:5173",  # Vite dev server default
        "http://localhost:5174",  # Alternative dev port
        "http://127.0.0.1:5173",  # Localhost alternative
        "http://127.0.0.1:5174",  # Localhost alternative
    ]
    
    # Add production origins from environment variable
    prod_origins = os.getenv("CORS_ORIGINS", "")
    if prod_origins:
        origins.extend([origin.strip() for origin in prod_origins.split(",")])
    
    return origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Accept",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers"
    ],
)

model_service: ModelService | None = None

# Include routers AFTER CORS middleware
app.include_router(predictions.router, prefix="/predict", tags=["predictions"], dependencies=[])
app.include_router(alerts.router, prefix="/alerts", tags=["alerts"], dependencies=[])
app.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"], dependencies=[])
app.include_router(feature.router, prefix="/feature", tags=["feature"], dependencies=[])
app.include_router(vitals.router, prefix="/vitals", tags=["vitals"], dependencies=[])
app.include_router(adherence.router, prefix="/adherence", tags=["adherence"], dependencies=[])
app.include_router(noshow.router, prefix="/noshow", tags=["noshow"], dependencies=[])
app.include_router(deterioration_risk.router, prefix="/risk", tags=["risk"], dependencies=[])
app.include_router(escalation.router, prefix="/escalation", tags=["escalation"], dependencies=[])
app.include_router(chatbot.router, prefix="/chatbot", tags=["chatbot"], dependencies=[])


@app.on_event("startup")
async def startup_event():
    ensure_synthetic_dataset()
    service = ModelService()
    set_model_service(service)


@app.get("/health")
def health_check():
    return {"status": "ok"}


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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
