"""
API Routes for Remote Vitals Monitoring
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional
from pydantic import BaseModel
import sys
import os

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

from services.vitals_monitoring import VitalsMonitoringService

router = APIRouter()
vitals_service = VitalsMonitoringService()

# Initialize with synthetic data on startup
vitals_service.generate_synthetic_vitals()

class PatientVitalsRequest(BaseModel):
    patient_id: str

class VitalsAnalysisRequest(BaseModel):
    patient_id: str
    hours_back: int = 24

@router.get("/overview")
def get_vitals_overview():
    """Get overview of all patients' vitals status."""
    try:
        overview = vitals_service.get_all_patients_overview()
        return {
            "status": "success",
            "data": overview,
            "total_patients": len(overview)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/patient-summary")
def get_patient_summary(request: PatientVitalsRequest):
    """Get comprehensive summary of patient vitals status."""
    try:
        summary = vitals_service.get_patient_summary(request.patient_id)
        return {
            "status": "success",
            "data": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trends")
def detect_abnormal_trends(request: VitalsAnalysisRequest):
    """Detect abnormal trends in patient vitals."""
    try:
        trends = vitals_service.detect_abnormal_trends(
            request.patient_id, 
            request.hours_back
        )
        return {
            "status": "success",
            "data": trends
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/missing-readings")
def check_missing_readings(request: VitalsAnalysisRequest):
    """Check for missing or infrequent readings."""
    try:
        missing = vitals_service.check_missing_readings(
            request.patient_id, 
            request.hours_back
        )
        return {
            "status": "success",
            "data": missing
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stability")
def generate_stability_indicators(request: VitalsAnalysisRequest):
    """Generate overall stability indicators for patient vitals."""
    try:
        stability = vitals_service.generate_stability_indicators(
            request.patient_id, 
            request.hours_back
        )
        return {
            "status": "success",
            "data": stability
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/raw-data")
def get_vitals_data(patient_id: Optional[str] = Query(None)):
    """Get raw vitals data for a patient or all patients."""
    try:
        if patient_id:
            patient_data = vitals_service.vitals_data[
                vitals_service.vitals_data['patient_id'] == patient_id
            ].to_dict('records')
        else:
            patient_data = vitals_service.vitals_data.to_dict('records')
        
        return {
            "status": "success",
            "data": patient_data,
            "count": len(patient_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
