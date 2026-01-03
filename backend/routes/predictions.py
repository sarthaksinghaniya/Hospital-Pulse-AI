from typing import List

from fastapi import APIRouter, Depends

from models.schemas import EmergencyPrediction, ICUPrediction, PredictionRequest, StaffPrediction, TimeSeriesPoint
from services.model_registry import get_model_service
from services.model_service import ModelService

router = APIRouter()


def get_service() -> ModelService:
    return get_model_service()


@router.post("/emergency", response_model=EmergencyPrediction)
async def predict_emergency(payload: PredictionRequest, service: ModelService = Depends(get_service)):
    forecast = service.predict_emergency(payload.horizon_hours)
    points: List[TimeSeriesPoint] = [TimeSeriesPoint(timestamp=dt, value=val) for dt, val in forecast]
    surge_prob = service.estimate_surge_probability(points)
    summary = service.llm.summarize_emergency(points)
    return EmergencyPrediction(forecast=points, surge_probability=surge_prob, summary=summary)


@router.post("/icu", response_model=ICUPrediction)
async def predict_icu(payload: PredictionRequest, service: ModelService = Depends(get_service)):
    forecast = service.predict_icu(payload.horizon_hours)
    points: List[TimeSeriesPoint] = [TimeSeriesPoint(timestamp=dt, value=val) for dt, val in forecast]
    peak_risk = service.estimate_peak_risk(points)
    summary = service.llm.summarize_icu(points)
    return ICUPrediction(required_beds=points, peak_risk=peak_risk, summary=summary)


@router.post("/staff", response_model=StaffPrediction)
async def predict_staff(payload: PredictionRequest, service: ModelService = Depends(get_service)):
    workload = service.predict_staff(payload.horizon_hours)
    return workload
