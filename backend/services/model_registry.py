from __future__ import annotations

from typing import Optional

from .model_service import ModelService
from .synthetic_data import ensure_synthetic_dataset

_model_service: Optional[ModelService] = None


def set_model_service(service: ModelService) -> None:
    global _model_service
    _model_service = service


def get_model_service() -> ModelService:
    global _model_service
    if _model_service is None:
        ensure_synthetic_dataset()
        _model_service = ModelService()
    return _model_service
