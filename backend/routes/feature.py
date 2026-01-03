from fastapi import APIRouter

from ..services.model_registry import get_model_service
from ..models.schemas import SurgeEarlyWarning, HopxChatRequest, HopxChatResponse

router = APIRouter()


@router.get("/surge-early-warning", response_model=SurgeEarlyWarning)
async def surge_early_warning():
    service = get_model_service()
    return service.surge_early_warning()


@router.post("/hopx-chat", response_model=HopxChatResponse)
async def hopx_chat(request: HopxChatRequest):
    service = get_model_service()
    return service.hopx_chat(request)
