from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class TimeSeriesPoint(BaseModel):
    timestamp: datetime
    value: float
    label: Optional[str] = None


class EmergencyPrediction(BaseModel):
    forecast: List[TimeSeriesPoint]
    surge_probability: float = Field(ge=0, le=1)
    summary: str


class ICUPrediction(BaseModel):
    required_beds: List[TimeSeriesPoint]
    peak_risk: float = Field(ge=0, le=1)
    summary: str


class StaffWorkload(BaseModel):
    shift: str
    risk_score: float = Field(ge=0, le=1)
    stress_note: str


class StaffPrediction(BaseModel):
    workload: List[StaffWorkload]
    summary: str


class Alert(BaseModel):
    message: str
    severity: str  # low | medium | high
    window: str


class Recommendation(BaseModel):
    action: str
    rationale: str
    priority: str  # low | medium | high


class PredictionRequest(BaseModel):
    horizon_hours: int = Field(168, description="How many hours ahead to predict")


class AlertsResponse(BaseModel):
    alerts: List[Alert]
    summary: str


class RecommendationsResponse(BaseModel):
    recommendations: List[Recommendation]
    summary: str


class SurgeEarlyWarning(BaseModel):
    score: float = Field(ge=0, le=1)
    risk_level: str  # low | medium | high
    surge_probability: float = Field(ge=0, le=1)
    icu_peak_risk: float = Field(ge=0, le=1)
    staff_max_risk: float = Field(ge=0, le=1)
    explanation: str
    actions: List[str]


class HopxChatRequest(BaseModel):
    message: str


class HopxChatResponse(BaseModel):
    reply: str
