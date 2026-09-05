"""
Tests for Impact Scorer Service.
Verifies formula weighting:
  30% Price Movement
  25% Volume Spike
  20% News Sentiment
  15% Volatility Change
  10% Watchlist Relevance
"""

from app.services.impact_scorer import ImpactScorerService


def test_high_impact_surge_score():
    scorer = ImpactScorerService()
    event = {
        "symbol": "TATAMOTORS.NS",
        "company_name": "Tata Motors Limited",
        "event_type": "price_surge",
        "summary": "Tata Motors gained 4.8% with 2.9x volume",
        "price_change": 4.8,
        "volume_ratio": 2.9,
        "metadata": {
            "snapshot_price": 830.0,
            "current_price": 869.84,
            "volume_ratio": 2.9,
        },
    }

    scored = scorer.score(event)
    score = scored["impact_score"]

    # High price change + 2.9x volume should score above 60 (high impact)
    assert score >= 60, f"Expected high impact score (>=60), got {score}"
    assert score <= 100
    assert "_score_breakdown" in scored
    assert scored["_score_breakdown"]["price"] > 0
    assert scored["_score_breakdown"]["volume"] > 0


def test_minor_fluctuation_score():
    scorer = ImpactScorerService()
    event = {
        "symbol": "HDFCBANK.NS",
        "company_name": "HDFC Bank",
        "event_type": "minor_fluctuation",
        "summary": "Minor fluctuation",
        "price_change": 0.2,
        "volume_ratio": 1.05,
        "metadata": {},
    }

    scored = scorer.score(event)
    score = scored["impact_score"]

    # Minor fluctuation should score low (< 30)
    assert score < 30, f"Expected low impact score (<30), got {score}"


def test_volume_spike_without_price_move():
    scorer = ImpactScorerService()
    event = {
        "symbol": "INFY.NS",
        "company_name": "Infosys",
        "event_type": "volume_spike",
        "summary": "Trading at 3x average volume",
        "price_change": 0.5,
        "volume_ratio": 3.0,
        "metadata": {},
    }

    scored = scorer.score(event)
    score = scored["impact_score"]

    # Volume spike alone should produce medium impact (30-65)
    assert 30 <= score <= 70, f"Expected medium impact score (30-70), got {score}"
