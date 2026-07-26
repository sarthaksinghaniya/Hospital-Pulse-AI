from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_noshow_model_insights():
    response = client.get("/noshow/model-insights")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["success", "error"]


def test_noshow_predict_default_flow():
    payload = {
        "patient_id": "test-1",
        "Age": 35,
        "Gender": "F",
        "waiting_days": 2,
        "scheduled_hour": 10,
        "scheduled_dayofweek": 2,
        "appointment_dayofweek": 3,
        "SMS_received": 1,
        "Scholarship": 0,
        "Hipertension": 0,
        "Diabetes": 0,
        "Alcoholism": 0,
        "Handcap": 0
    }

    response = client.post("/noshow/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "no_show_probability" in data["data"] or "data" in data


def test_escalation_check_triggers_empty():
    payload = {
        "patient_id": "test-patient",
        "current_risk_assessment": {"risk": "low"},
        "previous_risk_assessment": {"risk": "low"}
    }

    response = client.post("/escalation/check-triggers", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "created_escalations" in data["data"]
