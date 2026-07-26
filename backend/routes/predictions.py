from typing import List

from fastapi import APIRouter, Depends, HTTPException

from pydantic import BaseModel
from backend.models.schemas import EmergencyPrediction, ICUPrediction, PredictionRequest, StaffPrediction, TimeSeriesPoint
from backend.services.model_registry import get_model_service, set_model_service
from backend.services.model_service import ModelService
from backend.services.synthetic_data import ensure_synthetic_dataset

router = APIRouter()


class PatientRequest(BaseModel):
    age: int
    waiting_days: int
    sms_received: int


def get_service() -> ModelService:
    return get_model_service()


@router.post("")
async def predict_patient(request: PatientRequest):
    """Lightweight patient risk endpoint used by HopX frontend.

    Returns interpretable risk score with factors and recommendations.
    """
    risk = 0.67

    # Basic heuristic mirroring feature importance: waiting_days >> age >> sms_received
    if request.waiting_days > 14:
        risk += 0.15
    elif request.waiting_days < 3:
        risk -= 0.15

    if request.age < 30:
        risk += 0.08
    elif request.age > 60:
        risk -= 0.05

    if request.sms_received:
        risk -= 0.12
    else:
        risk += 0.1

    risk = max(0.0, min(risk, 0.99))

    factors = [
        "Waiting days high" if request.waiting_days > 7 else "Waiting days manageable",
        "Younger age increases risk" if request.age < 30 else "Age stabilizes attendance",
        "SMS reminder sent" if request.sms_received else "No SMS reminder",
    ]

    recommendations = [
        "Send reminder within 24h" if not request.sms_received else "Maintain reminders",
        "Offer sooner slot if waiting > 14 days" if request.waiting_days > 14 else "Confirm appointment time",
        "Flag for follow-up call if high risk",
    ]

    return {
        "risk": risk,
        "factors": factors,
        "recommendations": recommendations,
    }


@router.post("/emergency", response_model=EmergencyPrediction)
async def predict_emergency(payload: PredictionRequest, service: ModelService = Depends(get_service)):
    try:
        forecast = service.predict_emergency(payload.horizon_hours)
        points: List[TimeSeriesPoint] = [TimeSeriesPoint(timestamp=dt, value=val) for dt, val in forecast]
        surge_prob = service.estimate_surge_probability(points)
        summary = service.llm.summarize_emergency(points)
        return EmergencyPrediction(forecast=points, surge_probability=surge_prob, summary=summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting emergency: {str(e)}")


@router.post("/icu", response_model=ICUPrediction)
async def predict_icu(payload: PredictionRequest, service: ModelService = Depends(get_service)):
    try:
        forecast = service.predict_icu(payload.horizon_hours)
        points: List[TimeSeriesPoint] = [TimeSeriesPoint(timestamp=dt, value=val) for dt, val in forecast]
        peak_risk = service.estimate_peak_risk(points)
        summary = service.llm.summarize_icu(points)
        return ICUPrediction(required_beds=points, peak_risk=peak_risk, summary=summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting ICU: {str(e)}")


@router.post("/staff", response_model=StaffPrediction)
async def predict_staff(payload: PredictionRequest, service: ModelService = Depends(get_service)):
    try:
        workload = service.predict_staff(payload.horizon_hours)
        return workload
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting staff: {str(e)}")
