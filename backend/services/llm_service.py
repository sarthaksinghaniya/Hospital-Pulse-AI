from __future__ import annotations

import os
from typing import List, Optional

from openai import OpenAI

from ..models.schemas import Alert, Recommendation, TimeSeriesPoint, StaffWorkload


class LLMService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.enabled = bool(api_key)
        self.client: Optional[OpenAI] = OpenAI(api_key=api_key) if self.enabled else None
        # Default fallback model name; callers can override if needed
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def _complete(self, system_prompt: str, user_prompt: str, fallback: str) -> str:
        if not self.enabled or self.client is None:
            return fallback
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=200,
                temperature=0.3,
            )
            return resp.choices[0].message.content.strip()
        except Exception:
            return fallback

    def summarize_emergency(self, points: List[TimeSeriesPoint]) -> str:
        fallback = "ER forecast ready; monitor surge probability and top peaks in next 72h."
        if not points:
            return fallback
        peak = max(points, key=lambda p: p.value)
        system_prompt = """You are a clinical operations assistant. Be concise and actionable."""
        user_prompt = (
            "Summarize emergency load forecast. Peak {peak_val:.1f} around {ts}."
        ).format(peak_val=peak.value, ts=peak.timestamp.isoformat())
        return self._complete(system_prompt, user_prompt, fallback)

    def summarize_icu(self, points: List[TimeSeriesPoint]) -> str:
        fallback = "ICU forecast generated; prep contingency beds if peaks approach capacity."
        if not points:
            return fallback
        peak = max(points, key=lambda p: p.value)
        system_prompt = "You are an ICU ops assistant. Be concise and risk-aware."
        user_prompt = f"ICU peaks near {peak.value:.1f} beds at {peak.timestamp.isoformat()}. Give 1–2 prep tips."
        return self._complete(system_prompt, user_prompt, fallback)

    def summarize_staff(self, workload: List[StaffWorkload]) -> str:
        fallback = "Staff workload assessed; consider reinforcing high-risk shifts."
        if not workload:
            return fallback
        top = max(workload, key=lambda w: w.risk_score)
        system_prompt = "You advise nurse managers. Keep it brief and supportive."
        user_prompt = f"Highest stress shift: {top.shift} with risk {top.risk_score:.2f}. Provide a short mitigation." 
        return self._complete(system_prompt, user_prompt, fallback)

    def summarize_alerts(self, alerts: List[Alert]) -> str:
        fallback = "Alerts compiled; prioritize high-severity items first."
        if not alerts:
            return fallback
        critical = [a for a in alerts if a.severity == "high"]
        system_prompt = "You summarize hospital operational alerts in one sentence."
        user_prompt = f"We have {len(critical)} high and {len(alerts)} total alerts. Provide a one-line focus."
        return self._complete(system_prompt, user_prompt, fallback)

    def summarize_recommendations(self, recs: List[Recommendation]) -> str:
        fallback = "Recommendations ready; execute high-priority actions first."
        if not recs:
            return fallback
        high = [r for r in recs if r.priority == "high"]
        system_prompt = "You summarize operational recommendations in one line."
        user_prompt = f"There are {len(high)} high-priority actions out of {len(recs)}. Provide a concise directive."
        return self._complete(system_prompt, user_prompt, fallback)
