"""
Impact Scorer Service — assigns a 0–100 impact score to detected events.

Formula:
  Impact Score =
    30% Price Movement score
    25% Volume Spike score
    20% News Sentiment score
    15% Volatility Change score
    10% Watchlist Relevance score
"""

import math
from typing import Dict, Any
from app.core.config import settings


class ImpactScorerService:
    """Scores raw event dicts and returns them with an impact_score field."""

    def score(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Compute and attach impact_score to the event dict."""
        event_type = event.get("event_type", "minor_fluctuation")
        price_change = abs(event.get("price_change") or 0.0)
        volume_ratio = event.get("volume_ratio") or 1.0
        metadata = event.get("metadata", {}) or {}

        # ── Component scores (0–100) ───────────────────────────────────────
        price_score = self._price_score(price_change)
        volume_score = self._volume_score(volume_ratio)
        news_score = self._news_score(event_type, metadata)
        volatility_score = self._volatility_score(price_change, volume_ratio)
        relevance_score = self._relevance_score(event_type)

        # ── Weighted sum ───────────────────────────────────────────────────
        raw_score = (
            settings.WEIGHT_PRICE * price_score
            + settings.WEIGHT_VOLUME * volume_score
            + settings.WEIGHT_NEWS * news_score
            + settings.WEIGHT_VOLATILITY * volatility_score
            + settings.WEIGHT_WATCHLIST * relevance_score
        )

        impact_score = max(0, min(100, round(raw_score)))
        event["impact_score"] = impact_score
        event["_score_breakdown"] = {
            "price": round(price_score, 1),
            "volume": round(volume_score, 1),
            "news": round(news_score, 1),
            "volatility": round(volatility_score, 1),
            "relevance": round(relevance_score, 1),
        }
        return event

    # ── Scoring helpers ────────────────────────────────────────────────────

    def _price_score(self, price_change_pct: float) -> float:
        """
        Calibrated for equity markets (where 4-5% is near circuit):
        0.5% -> ~15
        2.0% -> ~50
        4.8% -> ~88
        8.0%+ -> ~98
        """
        if price_change_pct <= 0:
            return 0.0
        return min(100.0, 100.0 / (1.0 + math.exp(-0.9 * (price_change_pct - 2.2))))

    def _volume_score(self, volume_ratio: float) -> float:
        """
        1.0x -> 0
        2.0x -> 50
        2.9x -> ~95
        3.0x+ -> 100
        """
        if volume_ratio <= 1.0:
            return 0.0
        score = (volume_ratio - 1.0) / 2.0 * 100.0
        return max(0.0, min(100.0, score))

    def _news_score(self, event_type: str, metadata: dict) -> float:
        """Scores news impact based on catalyst metadata and event taxonomy."""
        if metadata.get("news") or metadata.get("catalyst"):
            return 88.0
        type_scores = {
            "price_surge": 70.0,
            "price_drop": 70.0,
            "volume_spike": 55.0,
            "news_event": 90.0,
            "volatility_increase": 60.0,
            "sector_movement": 45.0,
            "all_time_high": 95.0,
            "all_time_low": 95.0,
            "minor_fluctuation": 5.0,
        }
        return type_scores.get(event_type, 20.0)

    def _volatility_score(self, price_change_pct: float, volume_ratio: float) -> float:
        """Combined price movement and volume volatility proxy."""
        combined = (price_change_pct / 5.0) * (volume_ratio / 2.5) * 80.0
        return max(0.0, min(100.0, combined))

    def _relevance_score(self, event_type: str) -> float:
        """Watchlist relevance component score."""
        if event_type in ("all_time_high", "all_time_low", "news_event"):
            return 90.0
        if event_type in ("price_surge", "price_drop"):
            return 70.0
        if event_type == "volume_spike":
            return 50.0
        return 30.0
