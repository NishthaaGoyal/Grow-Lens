"""
Change Detection Service — compares snapshot data against current market data
and generates structured event objects.
"""

from typing import List, Dict, Any
from app.core.config import settings


class ChangeDetectionService:
    """
    Compares a previous snapshot against current market data
    and produces a list of raw events for scoring.
    """

    def detect(
        self,
        snapshot_items: List[Any],
        current_quotes: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Main detection method.
        Returns list of raw event dicts (unsorted, unscored).
        """
        events = []
        for snap_item in snapshot_items:
            symbol = snap_item.symbol
            current = current_quotes.get(symbol)
            if not current:
                continue

            snapshot_price = float(snap_item.price)
            current_price = current["price"]
            snapshot_volume = snap_item.volume
            current_volume = current["volume"]
            avg_volume = current.get("avg_volume") or snapshot_volume or 1

            # ── Price change since snapshot ────────────────────────────────
            if snapshot_price and snapshot_price != 0:
                price_change_pct = (current_price - snapshot_price) / snapshot_price * 100
            else:
                price_change_pct = 0.0

            # ── Volume ratio vs average ────────────────────────────────────
            volume_ratio = current_volume / avg_volume if avg_volume else 1.0

            # ── Detect event types ─────────────────────────────────────────
            detected = []

            if abs(price_change_pct) >= settings.PRICE_SURGE_THRESHOLD:
                event_type = "price_surge" if price_change_pct > 0 else "price_drop"
                direction = "gained" if price_change_pct > 0 else "dropped"
                detected.append({
                    "symbol": symbol,
                    "company_name": snap_item.company_name,
                    "event_type": event_type,
                    "summary": (
                        f"{snap_item.company_name} {direction} "
                        f"{abs(price_change_pct):.1f}% since your last visit "
                        f"(₹{snapshot_price:.0f} → ₹{current_price:.0f})"
                    ),
                    "price_change": round(price_change_pct, 4),
                    "volume_ratio": round(volume_ratio, 2),
                    "metadata": {
                        "snapshot_price": snapshot_price,
                        "current_price": current_price,
                        "snapshot_volume": snapshot_volume,
                        "current_volume": current_volume,
                        "avg_volume": avg_volume,
                    },
                })

            if volume_ratio >= settings.VOLUME_SPIKE_MULTIPLIER and abs(price_change_pct) < settings.PRICE_SURGE_THRESHOLD:
                # Standalone volume spike without a large price move
                detected.append({
                    "symbol": symbol,
                    "company_name": snap_item.company_name,
                    "event_type": "volume_spike",
                    "summary": (
                        f"{snap_item.company_name} is trading at "
                        f"{volume_ratio:.1f}× its average volume with a minor price move."
                    ),
                    "price_change": round(price_change_pct, 4),
                    "volume_ratio": round(volume_ratio, 2),
                    "metadata": {
                        "current_volume": current_volume,
                        "avg_volume": avg_volume,
                        "volume_ratio": round(volume_ratio, 2),
                    },
                })

            # ── No significant change — still include but mark minor ────────
            if not detected:
                detected.append({
                    "symbol": symbol,
                    "company_name": snap_item.company_name,
                    "event_type": "minor_fluctuation",
                    "summary": (
                        f"{snap_item.company_name} shows a minor change of "
                        f"{price_change_pct:+.2f}% with normal trading volume."
                    ),
                    "price_change": round(price_change_pct, 4),
                    "volume_ratio": round(volume_ratio, 2),
                    "metadata": {
                        "snapshot_price": snapshot_price,
                        "current_price": current_price,
                    },
                })

            events.extend(detected)

        return events
