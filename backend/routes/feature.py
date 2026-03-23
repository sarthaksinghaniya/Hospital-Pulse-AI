from fastapi import APIRouter

from backend.models.schemas import SurgeEarlyWarning, HopxChatRequest, HopxChatResponse
from backend.services.model_registry import get_model_service
from backend.services.model_service import ModelService

router = APIRouter()


@router.get("/surge-early-warning", response_model=SurgeEarlyWarning)
async def surge_early_warning():
    service = get_model_service()
    return service.surge_early_warning()


@router.post("/hopx-chat", response_model=HopxChatResponse)
async def hopx_chat(request: HopxChatRequest):
    service = get_model_service()
    return service.hopx_chat(request)


# backward compatibility for frontend that currently calls /feature/chat
@router.post("/chat", response_model=HopxChatResponse)
async def feature_chat(request: HopxChatRequest):
    service = get_model_service()
    return service.hopx_chat(request)
