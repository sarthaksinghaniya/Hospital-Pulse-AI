"""
API Routes for Adherence Nudging
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional
from pydantic import BaseModel
import sys
import os

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

from services.adherence_nudging import AdherenceNudgingService

router = APIRouter()
adherence_service = AdherenceNudgingService()

class AdherenceScoreRequest(BaseModel):
    patient_id: str

class PersonalizedNudgeRequest(BaseModel):
    patient_id: str
    patient_name: str = "Patient"

class AdherenceTrendsRequest(BaseModel):
    patient_id: str
    days_back: int = 30

@router.get("/adherence/population-overview")
def get_population_adherence_overview():
    """Get adherence overview for all patients."""
    try:
        overview = adherence_service.get_population_adherence_overview()
        return {
            "status": "success",
            "data": overview
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/adherence/score")
def compute_adherence_score(request: AdherenceScoreRequest):
    """Compute comprehensive adherence score for a patient."""
    try:
        score = adherence_service.compute_adherence_score(request.patient_id)
        return {
            "status": "success",
            "data": score
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/adherence/nudge")
def generate_personalized_nudge(request: PersonalizedNudgeRequest):
    """Generate personalized nudge based on adherence score."""
    try:
        # First get adherence score
        adherence_score = adherence_service.compute_adherence_score(request.patient_id)
        
        # Generate nudge
        nudge = adherence_service.generate_personalized_nudge(
            request.patient_id,
            adherence_score,
            request.patient_name
        )
        
        return {
            "status": "success",
            "data": {
                "adherence_score": adherence_score,
                "nudge": nudge
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/adherence/trends")
def track_adherence_trends(request: AdherenceTrendsRequest):
    """Track adherence trends over time for a patient."""
    try:
        trends = adherence_service.track_adherence_trends(
            request.patient_id,
            request.days_back
        )
        return {
            "status": "success",
            "data": trends
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/adherence/insights")
def get_adherence_insights(request: AdherenceScoreRequest):
    """Get comprehensive adherence insights for a patient."""
    try:
        insights = adherence_service.get_adherence_insights(request.patient_id)
        return {
            "status": "success",
            "data": insights
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/adherence/nudge-history")
def get_nudge_history(patient_id: Optional[str] = Query(None)):
    """Get nudge history for a patient or all patients."""
    try:
        if patient_id:
            history = adherence_service.nudge_history.get(patient_id, [])
        else:
            history = adherence_service.nudge_history
        
        return {
            "status": "success",
            "data": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
