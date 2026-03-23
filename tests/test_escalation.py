import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_get_escalation_triggers():
    """Test getting escalation triggers"""
    test_data = {
        "patient_id": "12345",
        "current_risk_assessment": {"risk_score": 0.8, "severity": "high"},
        "previous_risk_assessment": {"risk_score": 0.3, "severity": "low"}
    }
    response = client.post("/escalation/check-triggers", json=test_data)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "success"
    assert "data" in data

def test_create_escalation():
    """Test creating an escalation"""
    test_data = {
        "patient_id": "12345",
        "current_risk_assessment": {"risk_score": 0.9, "severity": "critical"},
        "previous_risk_assessment": {"risk_score": 0.4, "severity": "medium"}
    }
    response = client.post("/escalation/check-triggers", json=test_data)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "success"

def test_get_escalation_history():
    """Test getting escalation history"""
    response = client.get("/escalation/patient/12345")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "success"