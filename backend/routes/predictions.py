from typing import List

from fastapi import APIRouter, Depends, HTTPException

from backend.models.schemas import EmergencyPrediction, ICUPrediction, PredictionRequest, StaffPrediction, TimeSeriesPoint
from backend.services.model_registry import get_model_service, set_model_service
from backend.services.model_service import ModelService
from backend.services.synthetic_data import ensure_synthetic_dataset

router = APIRouter()


def get_service() -> ModelService:
    try:
        return get_model_service()
    except RuntimeError:
        # Auto-initialize if not already done
        ensure_synthetic_dataset()
        service = ModelService()
        set_model_service(service)
        return service


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
