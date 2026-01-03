# Surge Early-Warning Index (SEWI) Feature

## What it is
SEWI is a composite operational risk indicator that combines Emergency Department surge probability, ICU peak risk, and staff workload pressure into a single score (0–1). Lower is better; higher levels indicate impending overload.

## How it works
- **Inputs**: Reuses existing predictions for ER surge probability, ICU peak risk, and max staff stress over the next 72 hours.
- **Scoring formula**: `score = 0.4 * ER surge + 0.35 * ICU peak + 0.25 * staff max risk` (clipped 0–1).
- **Risk levels**:
  - Low: score < 0.35
  - Medium: 0.35 ≤ score < 0.65
  - High: score ≥ 0.65
- **Outputs**:
  - Composite score and risk level
  - Driver percentages (ER surge, ICU peak, staff pressure)
  - Plain-language explanation
  - Recommended actions (rule-based, interpretable)

## API endpoint
- **GET** `/feature/surge-early-warning`
- Returns JSON with `score`, `risk_level`, `surge_probability`, `icu_peak_risk`, `staff_max_risk`, `explanation`, `actions`.

## Why it matters
- Gives administrators a single, interpretable readiness metric.
- Prioritizes actions before ER crowding, ICU shortages, or staff burnout occur.
- Supports proactive surge planning and resource allocation.

## Example response
```json
{
  "score": 0.62,
  "risk_level": "medium",
  "surge_probability": 0.55,
  "icu_peak_risk": 0.60,
  "staff_max_risk": 0.50,
  "explanation": "ER surge probability 55%, ICU peak risk 60%, max staff stress 50%. Composite SEWI score 0.62.",
  "actions": [
    "Pre-position one extra staff for evening/night shifts.",
    "Audit ICU bed turnover and prepare rapid discharge protocols."
  ]
}
```

## Notes
- No patient identifiers; uses aggregated synthetic data.
- Rule-based actions ensure transparency and clinician trust.
- Integrated into the dashboard with real-time updates.
