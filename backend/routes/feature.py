from fastapi import APIRouter

from backend.models.schemas import SurgeEarlyWarning, HopxChatRequest, HopxChatResponse
from backend.services.model_registry import get_model_service, set_model_service
from backend.services.model_service import ModelService
from backend.services.synthetic_data import ensure_synthetic_dataset

router = APIRouter()


def get_service():
    try:
        return get_model_service()
    except RuntimeError:
        # Auto-initialize if not already done
        ensure_synthetic_dataset()
        service = ModelService()
        set_model_service(service)
        return service


@router.get("/surge-early-warning", response_model=SurgeEarlyWarning)
async def surge_early_warning():
    service = get_service()
    return service.surge_early_warning()


@router.post("/hopx-chat", response_model=HopxChatResponse)
async def hopx_chat(request: HopxChatRequest):
    service = get_service()
    return service.hopx_chat(request)


# backward compatibility for frontend that currently calls /feature/chat
@router.post("/chat", response_model=HopxChatResponse)
async def feature_chat(request: HopxChatRequest):
    service = get_service()
    return service.hopx_chat(request)
