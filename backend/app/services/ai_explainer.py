"""
AI Explainer Service — uses Gemini API to generate plain-English
explanations for market events ("Why it matters").
"""

from typing import Dict, Any, Optional
import google.generativeai as genai

from app.core.config import settings


class AIExplainerService:
    """Generates AI-powered explanations using Gemini."""

    def __init__(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
            self._available = True
        else:
            self._available = False
            print("[AIExplainerService] No GEMINI_API_KEY — using fallback explanations")

    async def explain(self, event: Dict[str, Any]) -> str:
        """Generate a beginner-friendly explanation for an event."""
        if not self._available:
            return self._fallback_explanation(event)

        prompt = self._build_prompt(event)
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"[AIExplainerService] Gemini error: {e}")
            return self._fallback_explanation(event)

    def _build_prompt(self, event: Dict[str, Any]) -> str:
        company = event.get("company_name", event.get("symbol", "This company"))
        event_type = event.get("event_type", "market event")
        price_change = event.get("price_change", 0)
        volume_ratio = event.get("volume_ratio", 1)
        summary = event.get("summary", "")
        score = event.get("impact_score", 0)

        return f"""You are a friendly financial analyst explaining stock market events to a retail investor in India who is new to investing.

Event Details:
- Company: {company}
- Event Type: {event_type}
- Price Change: {price_change:+.2f}% since last visit
- Volume: {volume_ratio:.1f}x average trading volume
- Impact Score: {score}/100
- Summary: {summary}

Write a clear, friendly, 2-3 sentence explanation of:
1. What happened
2. Why it might matter to the investor

Rules:
- Use simple language (no jargon like "MACD", "RSI", "basis points")
- Be factual and balanced — do not recommend buying or selling
- Keep it under 60 words
- Write in present tense
- Start with the most important insight

Response:"""

    def _fallback_explanation(self, event: Dict[str, Any]) -> str:
        """Return a template-based explanation when Gemini is unavailable."""
        event_type = event.get("event_type", "minor_fluctuation")
        company = event.get("company_name", "This stock")
        price_change = event.get("price_change", 0)
        volume_ratio = event.get("volume_ratio", 1.0)

        templates = {
            "price_surge": (
                f"{company} has moved up significantly ({price_change:+.1f}%) since your last visit. "
                f"{'Trading volume is ' + str(round(volume_ratio, 1)) + 'x normal, indicating strong investor interest.' if volume_ratio > 1.5 else 'Price movement appears relatively low-volume.'}"
            ),
            "price_drop": (
                f"{company} has declined {abs(price_change):.1f}% since you last checked. "
                f"{'The high trading volume (' + str(round(volume_ratio, 1)) + 'x average) suggests active selling pressure.' if volume_ratio > 1.5 else 'No unusual volume was recorded alongside this decline.'}"
            ),
            "volume_spike": (
                f"{company} is seeing unusually high trading activity — "
                f"{round(volume_ratio, 1)}x its average volume. "
                f"This often indicates increased investor interest even without a large price move."
            ),
            "minor_fluctuation": (
                f"{company} has shown only a small movement of {price_change:+.2f}% "
                f"with normal trading volume. No significant market event is detected."
            ),
        }
        return templates.get(event_type, f"{company} has experienced a market event. Review the details above.")


class MarketPulseGenerator:
    """Generates the Daily Market Pulse using Gemini."""

    def __init__(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
            self._available = True
        else:
            self._available = False

    async def generate_pulse(self, sector_data: Dict[str, float]) -> Dict[str, Any]:
        """Generate market pulse from sector performance data."""
        if not self._available:
            return self._fallback_pulse(sector_data)

        strongest = max(sector_data, key=sector_data.get) if sector_data else "Unknown"
        weakest = min(sector_data, key=sector_data.get) if sector_data else "Unknown"
        avg_performance = sum(sector_data.values()) / len(sector_data) if sector_data else 0

        mood = "Bullish" if avg_performance > 0.5 else "Bearish" if avg_performance < -0.5 else "Neutral"

        prompt = f"""You are a market analyst generating a brief daily market summary for Indian retail investors.

Sector Performance Today:
{chr(10).join(f"- {sector}: {change:+.2f}%" for sector, change in sector_data.items())}

Overall Market Mood: {mood}
Strongest Sector: {strongest} ({sector_data.get(strongest, 0):+.2f}%)
Weakest Sector: {weakest} ({sector_data.get(weakest, 0):+.2f}%)

Generate a 2-sentence narrative summary of today's market in plain language for a beginner investor.
Be factual. Do not give buy/sell recommendations.

Response (just the 2 sentences, no headers):"""

        try:
            response = await self.model.generate_content_async(prompt)
            narrative = response.text.strip()
        except Exception:
            narrative = self._fallback_narrative(mood, strongest, weakest)

        return {
            "market_mood": mood,
            "strongest_sector": strongest,
            "weakest_sector": weakest,
            "global_sentiment": "Bullish" if avg_performance > 1 else "Bearish" if avg_performance < -1 else "Mixed",
            "top_theme": f"{strongest} Rally" if sector_data.get(strongest, 0) > 1 else "Broad Market Movement",
            "ai_narrative": narrative,
            "raw_data": sector_data,
        }

    def _fallback_pulse(self, sector_data: Dict[str, float]) -> Dict[str, Any]:
        strongest = max(sector_data, key=sector_data.get) if sector_data else "Technology"
        weakest = min(sector_data, key=sector_data.get) if sector_data else "Pharma"
        avg = sum(sector_data.values()) / len(sector_data) if sector_data else 0
        mood = "Bullish" if avg > 0 else "Bearish"
        return {
            "market_mood": mood,
            "strongest_sector": strongest,
            "weakest_sector": weakest,
            "global_sentiment": "Mixed",
            "top_theme": f"{strongest} momentum",
            "ai_narrative": f"Markets are showing a {mood.lower()} trend today with {strongest} leading gains.",
            "raw_data": sector_data,
        }

    def _fallback_narrative(self, mood: str, strongest: str, weakest: str) -> str:
        return (
            f"Indian markets are trending {mood.lower()} today, with {strongest} "
            f"leading the pack while {weakest} faces some pressure. "
            f"Investors are advised to stay informed and review their portfolios."
        )
