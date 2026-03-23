import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_train_no_show_model():
    """Test training the no-show prediction model"""
    response = client.post("/noshow/train")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "success"

def test_predict_no_show():
    """Test predicting no-show probability"""
    # First ensure model is trained
    train_response = client.post("/noshow/train")
    assert train_response.status_code == 200
    
    test_data = {
        "patient_id": "12345",
        "Age": 35,
        "Gender": "F",
        "waiting_days": 5,
        "scheduled_hour": 10,
        "scheduled_dayofweek": 0,
        "appointment_dayofweek": 0,
        "SMS_received": 1,
        "Scholarship": 0,
        "Hipertension": 1,
        "Diabetes": 0,
        "Alcoholism": 0,
        "Handcap": 0
    }
    response = client.post("/noshow/predict", json=test_data)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "success"
    assert "data" in data
    # The response structure may vary, but it should contain prediction data
    prediction_data = data["data"]
    assert isinstance(prediction_data, dict)

def test_invalid_age():
    """Test validation for invalid age"""
    test_data = {
        "age": -5,  # Invalid age
        "gender": "F",
        "appointment_day": "Monday",
        "appointment_hour": 10,
        "diabetes": 0,
        "hypertension": 1,
        "alcoholism": 0,
        "handicap": 0,
        "sms_received": 1,
        "awaiting_time": 5
    }
    response = client.post("/noshow/predict", json=test_data)
    assert response.status_code == 422  # Validation error