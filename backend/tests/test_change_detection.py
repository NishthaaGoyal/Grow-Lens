"""
Tests for Change Detection Engine.
Verifies event extraction from snapshot comparisons.
"""

from app.services.change_detection import ChangeDetectionService


class MockSnapshotItem:
    def __init__(self, symbol, company_name, price, volume):
        self.symbol = symbol
        self.company_name = company_name
        self.price = price
        self.volume = volume


def test_detect_price_surge():
    engine = ChangeDetectionService()
    snapshot_items = [
        MockSnapshotItem("TATAMOTORS.NS", "Tata Motors Limited", 800.0, 1000000),
    ]
    current_quotes = {
        "TATAMOTORS.NS": {
            "symbol": "TATAMOTORS.NS",
            "price": 840.0,       # +5%
            "volume": 2500000,    # 2.5x volume
            "avg_volume": 1000000,
            "daily_change": 5.0,
        }
    }

    events = engine.detect(snapshot_items, current_quotes)
    assert len(events) == 1
    assert events[0]["event_type"] == "price_surge"
    assert events[0]["price_change"] == 5.0
    assert events[0]["volume_ratio"] == 2.5


def test_detect_minor_fluctuation():
    engine = ChangeDetectionService()
    snapshot_items = [
        MockSnapshotItem("TCS.NS", "TCS", 4000.0, 1000000),
    ]
    current_quotes = {
        "TCS.NS": {
            "symbol": "TCS.NS",
            "price": 4010.0,       # +0.25%
            "volume": 1050000,    # 1.05x
            "avg_volume": 1000000,
            "daily_change": 0.25,
        }
    }

    events = engine.detect(snapshot_items, current_quotes)
    assert len(events) == 1
    assert events[0]["event_type"] == "minor_fluctuation"
