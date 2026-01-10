"""
API Routes for No-Show Prediction
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional
from pydantic import BaseModel
import sys
import os

# Add the services directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

from services.no_show_prediction import NoShowPredictionService

router = APIRouter()
no_show_service = NoShowPredictionService()

class PatientDataRequest(BaseModel):
    patient_id: str
    Age: int
    Gender: str
    waiting_days: int = 1
    scheduled_hour: int = 10
    scheduled_dayofweek: int = 0
    appointment_dayofweek: int = 0
    SMS_received: int = 1
    Scholarship: int = 0
    Hipertension: int = 0
    Diabetes: int = 0
    Alcoholism: int = 0
    Handcap: int = 0

class BatchPredictionRequest(BaseModel):
    patients: List[PatientDataRequest]

@router.post("/noshow/train")
def train_no_show_model():
    """Train the no-show prediction model."""
    try:
        result = no_show_service.train_model()
        return {
            "status": "success" if result['status'] == 'success' else "error",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/noshow/predict")
def predict_no_show(request: PatientDataRequest):
    """Predict no-show probability for a single patient."""
    try:
        if not no_show_service.model_trained:
            # Try to load existing model
            load_result = no_show_service.load_model()
            if load_result['status'] != 'success':
                # Train model if not available
                no_show_service.train_model()
        
        patient_data = request.dict()
        prediction = no_show_service.predict_no_show(patient_data)
        
        return {
            "status": "success",
            "data": prediction
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/noshow/batch-predict")
def batch_predict_no_show(request: BatchPredictionRequest):
    """Predict no-show for multiple patients."""
    try:
        if not no_show_service.model_trained:
            # Try to load existing model
            load_result = no_show_service.load_model()
            if load_result['status'] != 'success':
                # Train model if not available
                no_show_service.train_model()
        
        patients_data = [patient.dict() for patient in request.patients]
        predictions = no_show_service.batch_predict(patients_data)
        
        return {
            "status": "success",
            "data": {
                "predictions": predictions,
                "total_patients": len(predictions)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/noshow/model-insights")
def get_model_insights():
    """Get insights about the trained model."""
    try:
        insights = no_show_service.get_model_insights()
        return {
            "status": "success",
            "data": insights
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/noshow/feature-importance")
def get_feature_importance():
    """Get feature importance from the trained model."""
    try:
        if not no_show_service.model_trained:
            return {
                "status": "error",
                "message": "Model not trained yet"
            }
        
        return {
            "status": "success",
            "data": {
                "feature_importance": no_show_service.feature_importance,
                "top_features": list(no_show_service.feature_importance.keys())[:10]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/noshow/load-model")
def load_trained_model():
    """Load a previously trained model."""
    try:
        result = no_show_service.load_model()
        return {
            "status": result['status'],
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
