import asyncio
from dataclasses import dataclass
from typing import Dict, List, Optional

from limitless_client import LimitlessClient
from config import Config


@dataclass
class MarketInfo:
    market_id: str
    title: str
    yes_price: float
    no_price: float
    target_price: float
    expiry_time: str


class MarketDiscovery:
    def __init__(self, client: LimitlessClient, config: Config, logger):
        self._client = client
        self._config = config
        self._logger = logger
        self._markets: Dict[str, MarketInfo] = {}
        self._lock = asyncio.Lock()

    def _is_btc_market(self, title: str) -> bool:
        t = title.lower()
        return "btc" in t or "bitcoin" in t

    def _is_1h_market(self, title: str) -> bool:
        t = title.lower()
        return "1h" in t or "1 hour" in t

    async def refresh_markets(self):
        markets_raw = await self._client.get_markets()
        filtered: Dict[str, MarketInfo] = {}
        for m in markets_raw:
            try:
                title = str(m.get("title") or m.get("name") or "")
                status = str(m.get("status", "")).lower()
                if status not in ("active", "open", "trading"):
                    continue
                if not self._is_btc_market(title):
                    continue
                if not self._is_1h_market(title):
                    continue

                market_id = str(m.get("id") or m.get("market_id"))
                if not market_id:
                    continue

                yes_price = float(m.get("yes_price") or m.get("price_yes") or m.get("yes") or m.get("bid_yes"))
                no_price = float(m.get("no_price") or m.get("price_no") or m.get("no") or m.get("bid_no") or (1.0 - yes_price))
                target_price = float(m.get("target_price") or m.get("strike_price") or m.get("target"))
                expiry_time = str(m.get("expiry_time") or m.get("expiration") or m.get("end_time") or "")

                mi = MarketInfo(
                    market_id=market_id,
                    title=title,
                    yes_price=yes_price,
                    no_price=no_price,
                    target_price=target_price,
                    expiry_time=expiry_time,
                )
                filtered[market_id] = mi
            except Exception as e:
                self._logger.error(f"Error parsing market: {e}")

        async with self._lock:
            self._markets = filtered

        self._logger.info(f"Discovered {len(filtered)} active BTC 1H markets")

    async def get_markets(self) -> List[MarketInfo]:
        async with self._lock:
            return list(self._markets.values())
