"""
Market Data Service — fetches real-time stock quotes via yfinance.
"""

import asyncio
from typing import Dict, List, Any, Optional
import yfinance as yf


class MarketDataService:
    """Fetches current market quotes for a list of symbols."""

    async def get_quotes(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Fetch current quotes for all symbols.
        Returns a dict keyed by symbol.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._fetch_quotes_sync, symbols)

    def _fetch_quotes_sync(self, symbols: List[str]) -> Dict[str, Any]:
        """Synchronous fetch using yfinance (runs in thread pool)."""
        if not symbols:
            return {}

        results: Dict[str, Any] = {}
        try:
            tickers = yf.Tickers(" ".join(symbols))
            for symbol in symbols:
                try:
                    ticker = tickers.tickers.get(symbol)
                    if not ticker:
                        ticker = yf.Ticker(symbol)

                    info = ticker.fast_info
                    hist = ticker.history(period="2d")

                    if hist.empty:
                        results[symbol] = self._fallback_quote(symbol)
                        continue

                    current_price = float(info.last_price) if hasattr(info, "last_price") and info.last_price else float(hist["Close"].iloc[-1])
                    prev_close = float(hist["Close"].iloc[-2]) if len(hist) > 1 else current_price
                    volume = int(hist["Volume"].iloc[-1]) if not hist["Volume"].empty else 0
                    avg_volume = int(info.three_month_average_volume) if hasattr(info, "three_month_average_volume") and info.three_month_average_volume else volume

                    daily_change_abs = current_price - prev_close
                    daily_change_pct = (daily_change_abs / prev_close * 100) if prev_close != 0 else 0

                    results[symbol] = {
                        "symbol": symbol,
                        "company_name": getattr(info, "quote_type", symbol),
                        "price": round(current_price, 4),
                        "daily_change": round(daily_change_pct, 4),
                        "daily_change_abs": round(daily_change_abs, 4),
                        "volume": volume,
                        "avg_volume": avg_volume,
                        "market_cap": getattr(info, "market_cap", None),
                        "high_52w": getattr(info, "year_high", None),
                        "low_52w": getattr(info, "year_low", None),
                    }
                except Exception as e:
                    print(f"[MarketDataService] Error fetching {symbol}: {e}")
                    results[symbol] = self._fallback_quote(symbol)

        except Exception as e:
            print(f"[MarketDataService] Batch fetch error: {e}")
            for symbol in symbols:
                results[symbol] = self._fallback_quote(symbol)

        return results

    def _fallback_quote(self, symbol: str) -> Dict[str, Any]:
        """Return demo/mock data when real data is unavailable (dev mode)."""
        import random
        base_prices = {
            "INFY.NS": 1842.0, "TCS.NS": 4105.0, "WIPRO.NS": 489.0,
            "TATAMOTORS.NS": 872.0, "M&M.NS": 3091.0, "OLECTRA.NS": 1432.0,
            "HDFCBANK.NS": 1745.0, "RELIANCE.NS": 2987.0,
        }
        base = base_prices.get(symbol, 1000.0)
        change_pct = random.uniform(-5.0, 5.0)
        price = base * (1 + change_pct / 100)
        volume = random.randint(500_000, 5_000_000)
        avg_volume = random.randint(1_000_000, 3_000_000)

        return {
            "symbol": symbol,
            "company_name": symbol.replace(".NS", ""),
            "price": round(price, 2),
            "daily_change": round(change_pct, 4),
            "daily_change_abs": round(price - base, 4),
            "volume": volume,
            "avg_volume": avg_volume,
            "market_cap": None,
            "high_52w": None,
            "low_52w": None,
            "_is_mock": True,
        }

    async def get_sector_performance(self) -> Dict[str, float]:
        """Get approximate sector performance for Market Pulse."""
        sector_etfs = {
            "Technology": "^CNXIT",
            "Banking": "^NSEBANK",
            "Auto": "NIFTYAUTO.NS",
            "Pharma": "^CNXPHARMA",
            "FMCG": "^CNXFMCG",
            "Energy": "^CNXENERGY",
        }
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._fetch_sector_sync, sector_etfs)

    def _fetch_sector_sync(self, sector_etfs: Dict[str, str]) -> Dict[str, float]:
        performance = {}
        for sector, ticker_sym in sector_etfs.items():
            try:
                t = yf.Ticker(ticker_sym)
                hist = t.history(period="2d")
                if len(hist) >= 2:
                    change = (hist["Close"].iloc[-1] - hist["Close"].iloc[-2]) / hist["Close"].iloc[-2] * 100
                    performance[sector] = round(float(change), 2)
                else:
                    performance[sector] = 0.0
            except Exception:
                performance[sector] = 0.0
        return performance
