"""
Production-ready no-show prediction endpoint using pre-trained model artifacts.
"""
from pathlib import Path
from typing import List

import joblib
import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator

# Load serialized pipeline + threshold once at import time
MODEL_PATH = Path(__file__).resolve().parents[2] / "outputs" / "best_model.pkl"

try:
    artifact = joblib.load(MODEL_PATH)
    _pipeline = artifact.get("model")
    _threshold = float(artifact.get("threshold", 0.5))
except Exception as exc:  # pragma: no cover - defensive load guard
    _pipeline = None
    _threshold = 0.5
    _load_error = exc
else:
    _load_error = None

router = APIRouter()


class PatientPayload(BaseModel):
    gender: str = Field(..., description="Gender as M/F")
    age: int = Field(..., ge=0, le=120)
    neighbourhood: str = Field(..., description="Patient neighbourhood")
    scholarship: int = Field(0, ge=0, le=1)
    hipertension: int = Field(0, ge=0, le=1)
    diabetes: int = Field(0, ge=0, le=1)
    alcoholism: int = Field(0, ge=0, le=1)
    handcap: int = Field(0, ge=0, le=1)
    sms_received: int = Field(0, ge=0, le=1)
    waiting_days: int = Field(..., ge=0, description="Days between scheduling and appointment")

    @validator("gender")
    def validate_gender(cls, v: str) -> str:
        v = v.strip().upper()
        if v not in {"M", "F"}:
            raise ValueError("gender must be 'M' or 'F'")
        return v

    @validator("neighbourhood")
    def validate_neighbourhood(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("neighbourhood cannot be empty")
        return v


def _ensure_model_loaded():
    if _pipeline is None:
        err = _load_error or "Model failed to load"
        raise HTTPException(status_code=500, detail=f"Model unavailable: {err}")
    return _pipeline


def _top_factors(model, df_row) -> List[str]:
    try:
        preprocess = model.named_steps.get("preprocess")
        estimator = model.named_steps.get("model")
        if preprocess is None or estimator is None:
            return []

        preprocess_output = preprocess.transform(df_row)
        feature_names = preprocess.get_feature_names_out()

        if hasattr(estimator, "feature_importances_"):
            scores = estimator.feature_importances_
        elif hasattr(estimator, "coef_"):
            scores = abs(estimator.coef_).ravel()
        else:
            return []

        pairs = sorted(zip(feature_names, scores), key=lambda x: x[1], reverse=True)[:3]

        readable = []
        for name, _ in pairs:
            clean = name.split("__")[-1]
            if "waiting_days" in clean:
                readable.append("Long wait time raises no-show risk")
            elif "sms_received" in clean:
                readable.append("Reminder SMS lowers risk when sent")
            elif "age" in clean:
                readable.append("Age group effect on attendance")
            elif "gender" in clean:
                readable.append("Gender correlation with attendance")
            elif "neighbourhood" in clean:
                readable.append("Neighbourhood risk signal")
            else:
                readable.append(clean.replace("_", " "))
        return readable
    except Exception:
        return []


def _recommendation(prob: float, df_row: pd.DataFrame) -> str:
    """Translate probability + key features into an actionable next step."""
    pct = prob * 100
    base = (
        "⚠️ High risk of no-show. Recommend reminder call or rescheduling."
        if pct > 60
        else "⚠️ Moderate risk. Consider SMS reminder."
        if pct >= 30
        else "✅ Low risk. No action needed."
    )

    # Advanced context from features
    msgs = []
    waiting = df_row.get("waiting_days")
    age = df_row.get("age")
    if waiting is not None and waiting.iloc[0] >= 7:
        msgs.append("Reduce scheduling delay")
    if age is not None and age.iloc[0] >= 65:
        msgs.append("Offer assistance / follow-up for elderly")

    if msgs:
        base += " " + " ".join(msgs)
    return base


@router.post("/predict", summary="Predict patient no-show probability")
async def predict(payload: PatientPayload):
    model = _ensure_model_loaded()
    df = pd.DataFrame([payload.dict()])

    try:
        prob = float(model.predict_proba(df)[:, 1][0])
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Inference failed: {exc}")

    risk = "High" if prob >= _threshold else "Low"
    factors = _top_factors(model, df)
    insight = factors[0] if factors else "Model-driven factors applied"
    recommendation = _recommendation(prob, df)

    return {
        "probability": round(prob * 100, 2),
        "risk": risk,
        "threshold": _threshold,
        "insight": insight,
        "top_factors": factors,
        "recommendation": recommendation,
    }
