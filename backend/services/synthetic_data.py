from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "synthetic_data.csv"


def _generate_hourly_rows(days: int = 90) -> pd.DataFrame:
    np.random.seed(42)
    start = datetime.utcnow() - timedelta(days=days)
    rows = []
    for i in range(days * 24):
        ts = start + timedelta(hours=i)
        hour = ts.hour
        dow = ts.weekday()
        month = ts.month
        base_er = 30 + 10 * np.sin(2 * np.pi * hour / 24) + 5 * np.cos(2 * np.pi * dow / 7)
        seasonality = 4 * np.sin(2 * np.pi * month / 12)
        weather_heat_index = np.clip(20 + 10 * np.sin(2 * np.pi * month / 12) + np.random.normal(0, 2), 10, 45)
        rain_flag = 1 if np.random.rand() < 0.2 else 0
        disease_trend = np.clip(0.5 + 0.3 * np.sin(2 * np.pi * month / 12) + np.random.normal(0, 0.1), 0, 1)
        holiday = 1 if dow in (5, 6) else 0
        er_admissions = max(5, int(base_er + seasonality + np.random.normal(0, 3)))
        icu_occupancy = max(3, int(er_admissions * (0.25 + 0.1 * disease_trend) + np.random.normal(0, 2)))
        staff_on_shift = int(20 + 3 * np.sin(2 * np.pi * hour / 24) + 2 * np.cos(2 * np.pi * dow / 7) + np.random.normal(0, 1))
        bed_available = max(5, 60 - icu_occupancy + int(np.random.normal(0, 2)))
        # Additional realistic fields
        ambulance_arrivals = max(0, int(np.random.poisson(2 + 0.5 * (hour >= 8 and hour <= 20))))
        avg_patient_age = round(np.clip(np.random.normal(55, 15), 20, 90), 1)
        flu_like_cases = int(np.random.poisson(1 + 0.2 * disease_trend * 10))
        surgical_cases = int(np.random.poisson(0.8 + 0.1 * (dow < 5)))
        discharge_rate = round(np.clip(np.random.normal(0.12, 0.03), 0.05, 0.25), 3)

        rows.append(
            {
                "timestamp": ts.isoformat(),
                "er_admissions": er_admissions,
                "icu_occupancy": icu_occupancy,
                "staff_on_shift": staff_on_shift,
                "avg_handling_time": round(np.clip(np.random.normal(2.5, 0.4), 1.5, 4.0), 2),
                "weather_heat_index": round(weather_heat_index, 2),
                "rain_flag": rain_flag,
                "disease_trend": round(disease_trend, 2),
                "holiday": holiday,
                "bed_available": bed_available,
                "ambulance_arrivals": ambulance_arrivals,
                "avg_patient_age": avg_patient_age,
                "flu_like_cases": flu_like_cases,
                "surgical_cases": surgical_cases,
                "discharge_rate": discharge_rate,
            }
        )

    return pd.DataFrame(rows)


def ensure_synthetic_dataset() -> Tuple[Path, pd.DataFrame]:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DATA_PATH.exists():
        df = pd.read_csv(DATA_PATH, parse_dates=["timestamp"])
        # If existing dataset is shorter than 90 days, regenerate
        if len(df) < 90 * 24:
            df = _generate_hourly_rows(90)
            df.to_csv(DATA_PATH, index=False)
        return DATA_PATH, df

    df = _generate_hourly_rows(90)
    df.to_csv(DATA_PATH, index=False)
    return DATA_PATH, df
