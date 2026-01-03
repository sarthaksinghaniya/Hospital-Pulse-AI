from fastapi import APIRouter

from models.schemas import AlertsResponse
from services.model_registry import get_model_service
from services.model_service import ModelService

router = APIRouter()


@router.get("", response_model=AlertsResponse)
async def list_alerts():
    service = get_model_service()
    alerts = service.generate_alerts()
    summary = service.llm.summarize_alerts(alerts)
    return AlertsResponse(alerts=alerts, summary=summary)
