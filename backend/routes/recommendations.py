from fastapi import APIRouter

from models.schemas import RecommendationsResponse
from services.model_registry import get_model_service
from services.model_service import ModelService

router = APIRouter()


@router.get("", response_model=RecommendationsResponse)
async def list_recommendations():
    service = get_model_service()
    recs = service.generate_recommendations()
    summary = service.llm.summarize_recommendations(recs)
    return RecommendationsResponse(recommendations=recs, summary=summary)
