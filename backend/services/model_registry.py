from __future__ import annotations

from typing import Optional

from .model_service import ModelService

_model_service: Optional[ModelService] = None


def set_model_service(service: ModelService) -> None:
    global _model_service
    _model_service = service


def get_model_service() -> ModelService:
    if _model_service is None:
        raise RuntimeError("ModelService not initialized yet")
    return _model_service
