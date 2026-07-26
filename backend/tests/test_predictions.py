import pytest
from fastapi.testclient import TestClient
from backend.main import app

def test_predict_emergency(client: TestClient):
    response = client.post("/predict/emergency", json={"horizon_hours": 24})
    assert response.status_code == 200
    data = response.json()
    assert "forecast" in data
    assert "surge_probability" in data
    assert "summary" in data

def test_predict_icu(client: TestClient):
    response = client.post("/predict/icu", json={"horizon_hours": 24})
    assert response.status_code == 200
    data = response.json()
    assert "required_beds" in data
    assert "peak_risk" in data
    assert "summary" in data

def test_predict_staff(client: TestClient):
    response = client.post("/predict/staff", json={"horizon_hours": 24})
    assert response.status_code == 200
    data = response.json()
    assert "workload" in data


def test_hopx_chat_sewi(client: TestClient):
    response = client.post("/feature/hopx-chat", json={"message": "Tell me about SEWI"})
    assert response.status_code == 200
    data = response.json()    
    assert "reply" in data
    assert "SEWI" in data["reply"]