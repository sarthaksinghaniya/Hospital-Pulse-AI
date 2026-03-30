import pytest
from fastapi.testclient import TestClient
from main import app
from backend.services.model_service import ModelService
from backend.services.model_registry import set_model_service
from backend.services.synthetic_data import ensure_synthetic_dataset

@pytest.fixture(scope="session")
def setup_model_service():
    """Initialize ModelService once for all tests"""
    ensure_synthetic_dataset()
    service = ModelService()
    set_model_service(service)

@pytest.fixture
def client(setup_model_service):
    return TestClient(app)