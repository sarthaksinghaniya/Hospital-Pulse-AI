"""
API Routes for No-Show Prediction
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator

from backend.services.no_show_prediction import NoShowPredictionService

router = APIRouter()
no_show_service = NoShowPredictionService()

class PatientDataRequest(BaseModel):
    patient_id: str = Field("", description="Patient identifier")
    Age: int = Field(..., ge=0, le=150, description="Patient age")
    Gender: str = Field(..., description="Patient gender (M/F)")
    waiting_days: int = Field(1, ge=0, description="Days until appointment")
    scheduled_hour: int = Field(10, ge=0, le=23, description="Scheduled hour (0-23)")
    scheduled_dayofweek: int = Field(0, ge=0, le=6, description="Scheduled day of week (0-6, 0=Monday)")
    appointment_dayofweek: int = Field(0, ge=0, le=6, description="Appointment day of week (0-6, 0=Monday)")
    SMS_received: int = Field(1, ge=0, le=1, description="SMS received (0=No, 1=Yes)")
    Scholarship: int = Field(0, ge=0, le=1, description="Scholarship (0=No, 1=Yes)")
    Hipertension: int = Field(0, ge=0, le=1, description="Hypertension (0=No, 1=Yes)")
    Diabetes: int = Field(0, ge=0, le=1, description="Diabetes (0=No, 1=Yes)")
    Alcoholism: int = Field(0, ge=0, le=1, description="Alcoholism (0=No, 1=Yes)")
    Handcap: int = Field(0, ge=0, le=1, description="Handicap (0=No, 1=Yes)")
    
    @validator('Gender')
    def validate_gender(cls, v):
        if v not in ['M', 'F', 'm', 'f']:
            raise ValueError('Gender must be M or F')
        return v.upper()
    
    @validator('patient_id')
    def validate_patient_id(cls, v):
        if not v:
            return 'UNKNOWN'
        return str(v)

class BatchPredictionRequest(BaseModel):
    patients: List[PatientDataRequest]

@router.post("/train")
def train_no_show_model():
    """Train the no-show prediction model."""
    try:
        result = no_show_service.train_model()
        return {
            "status": "success" if result['status'] == 'success' else "error",
            "data": _serialize_value(result)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _serialize_value(value):
    """Serialize numpy types and other objects to JSON-serializable types."""
    try:
        # Handle numpy types
        import numpy as np
        if isinstance(value, (np.integer, np.floating)):
            return float(value)
        elif isinstance(value, np.ndarray):
            return value.tolist()
        elif hasattr(value, '__dict__'):
            # Handle objects with __dict__ attribute
            return {k: _serialize_value(v) for k, v in value.__dict__.items()}
        elif isinstance(value, dict):
            return {k: _serialize_value(v) for k, v in value.items()}
        elif isinstance(value, (list, tuple)):
            return [_serialize_value(item) for item in value]
        else:
            return value
    except:
        return str(value)

def _serialize_prediction(prediction):
    """Serialize prediction result to JSON-serializable format."""
    return {
        "patient_id": str(prediction.get('patient_id', 'Unknown')),
        "probability": float(prediction.get('probability', 0)),
        "risk_level": str(prediction.get('risk_level', 'Low')),
        "risk_category": str(prediction.get('risk_category', 'Low')),
        "color_indicator": str(prediction.get('color_indicator', 'green')),
        "confidence": float(prediction.get('confidence', 0)),
        "contributing_factors": _serialize_value(prediction.get('contributing_factors', [])),
        "recommendations": _serialize_value(prediction.get('recommendations', [])),
        "feature_importance": _serialize_value(prediction.get('feature_importance', {})),
        "predicted_at": str(prediction.get('predicted_at', ''))
    }

@router.post("/predict")
def predict_no_show(request: PatientDataRequest):
    """Predict no-show probability for a single patient."""
    try:
        if not no_show_service.model_trained:
            # Try to load existing model
            load_result = no_show_service.load_model()
            if load_result['status'] != 'success':
                # Train model if not available
                no_show_service.train_model()
        
        patient_data = request.model_dump()
        prediction = no_show_service.predict_no_show(patient_data)
        
        return {
            "status": "success",
            "data": _serialize_prediction(prediction)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-predict")
def batch_predict_no_show(request: BatchPredictionRequest):
    """Predict no-show for multiple patients."""
    try:
        if not no_show_service.model_trained:
            # Try to load existing model
            load_result = no_show_service.load_model()
            if load_result['status'] != 'success':
                # Train model if not available
                no_show_service.train_model()
        
        patients_data = [patient.model_dump() for patient in request.patients]
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

@router.get("/model-insights")
def get_model_insights():
    """Get insights about the trained model."""
    try:
        insights = no_show_service.get_model_insights()
        return {
            "status": "success",
            "data": _serialize_value(insights)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/feature-importance")
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
                "feature_importance": _serialize_value(no_show_service.feature_importance),
                "top_features": _serialize_value(list(no_show_service.feature_importance.keys())[:10])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/load-model")
def load_trained_model():
    """Load a previously trained model."""
    try:
        result = no_show_service.load_model()
        return {
            "status": result['status'],
            "data": _serialize_value(result)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
