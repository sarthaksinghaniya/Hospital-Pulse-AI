"""
API Routes for Patient Deterioration Risk Assessment
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional
from pydantic import BaseModel
import sys
import os

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

from services.deterioration_risk import PatientDeteriorationRiskService
from services.vitals_monitoring import VitalsMonitoringService
from services.adherence_nudging import AdherenceNudgingService
from services.no_show_prediction import NoShowPredictionService

router = APIRouter()
risk_service = PatientDeteriorationRiskService()
vitals_service = VitalsMonitoringService()
adherence_service = AdherenceNudgingService()
no_show_service = NoShowPredictionService()

# Initialize services
vitals_service.generate_synthetic_vitals()

class PatientRiskRequest(BaseModel):
    patient_id: str
    age: int
    gender: str
    chronic_conditions: Dict = {}
    waiting_days: int = 3
    sms_received: int = 1
    scholarship: int = 0
    hypertension: int = 0
    diabetes: int = 0
    alcoholism: int = 0
    handcap: int = 0

class PopulationRiskRequest(BaseModel):
    patient_risk_scores: List[Dict]

class RiskTrendsRequest(BaseModel):
    patient_id: str
    historical_assessments: List[Dict]

@router.post("/risk/assess")
def calculate_overall_risk_score(request: PatientRiskRequest):
    """Calculate comprehensive deterioration risk score for a patient."""
    try:
        patient_data = request.dict()
        
        # Calculate risk score
        risk_assessment = risk_service.calculate_overall_risk_score(
            request.patient_id,
            patient_data,
            vitals_service,
            adherence_service,
            no_show_service
        )
        
        return {
            "status": "success",
            "data": risk_assessment
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/risk/population-overview")
def get_population_risk_overview(request: PopulationRiskRequest):
    """Get overview of risk distribution across patient population."""
    try:
        overview = risk_service.get_population_risk_overview(request.patient_risk_scores)
        return {
            "status": "success",
            "data": overview
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/risk/trends")
def track_risk_trends(request: RiskTrendsRequest):
    """Track risk trends for a specific patient over time."""
    try:
        trends = risk_service.track_risk_trends(
            request.patient_id,
            request.historical_assessments
        )
        return {
            "status": "success",
            "data": trends
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/risk/thresholds")
def get_risk_thresholds():
    """Get current risk thresholds used for categorization."""
    try:
        return {
            "status": "success",
            "data": {
                "risk_thresholds": risk_service.risk_thresholds,
                "risk_weights": risk_service.risk_weights
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/risk/vitals-component")
def calculate_vitals_risk(patient_id: str, stability_score: float, vitals_trends: Dict):
    """Calculate vitals component of risk score."""
    try:
        vitals_risk = risk_service.calculate_vitals_risk(stability_score, vitals_trends)
        return {
            "status": "success",
            "data": vitals_risk
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/risk/chronic-component")
def calculate_chronic_conditions_risk(patient_data: Dict):
    """Calculate chronic conditions component of risk score."""
    try:
        chronic_risk = risk_service.calculate_chronic_conditions_risk(patient_data)
        return {
            "status": "success",
            "data": chronic_risk
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/risk/adherence-component")
def calculate_adherence_risk(adherence_score: Dict):
    """Calculate adherence component of risk score."""
    try:
        adherence_risk = risk_service.calculate_adherence_risk(adherence_score)
        return {
            "status": "success",
            "data": adherence_risk
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/risk/noshow-component")
def calculate_no_show_risk(no_show_prediction: Dict):
    """Calculate no-show component of risk score."""
    try:
        no_show_risk = risk_service.calculate_no_show_risk(no_show_prediction)
        return {
            "status": "success",
            "data": no_show_risk
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
