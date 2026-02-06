import asyncio
from typing import Any, Dict, List, Optional

from limitless_sdk import Limitless

from config import Config


class LimitlessClient:
    def __init__(self, config: Config, logger):
        self._config = config
        self._logger = logger
        self._client = Limitless(api_key=config.limitless_api_key)

    async def _call(self, func, *args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)

    async def get_markets(self) -> List[Dict[str, Any]]:
        try:
            markets = await self._call(self._client.get_markets)
            return markets or []
        except Exception as e:
            self._logger.error(f"Error fetching markets from Limitless: {e}")
            return []

    async def get_market(self, market_id: str) -> Optional[Dict[str, Any]]:
        try:
            return await self._call(self._client.get_market, market_id)
        except Exception as e:
            self._logger.error(f"Error fetching market {market_id}: {e}")
            return None

    async def get_balance(self) -> float:
        try:
            balance_info = await self._call(self._client.get_balance)
            if isinstance(balance_info, dict):
                for key in ("available", "balance", "free"):
                    if key in balance_info:
                        return float(balance_info[key])
            return float(balance_info)
        except Exception as e:
            self._logger.error(f"Error fetching balance: {e}")
            return 0.0

    async def buy_yes(self, market_id: str, amount: float) -> Optional[Dict[str, Any]]:
        try:
            self._logger.info(f"Sending buy_yes order: market={market_id} amount={amount}")
            return await self._call(self._client.buy_yes, market_id, amount)
        except Exception as e:
            self._logger.error(f"Error executing buy_yes on {market_id}: {e}")
            return None

    async def sell_yes(self, market_id: str, amount: float) -> Optional[Dict[str, Any]]:
        try:
            self._logger.info(f"Sending sell_yes order: market={market_id} amount={amount}")
            return await self._call(self._client.sell_yes, market_id, amount)
        except Exception as e:
            self._logger.error(f"Error executing sell_yes on {market_id}: {e}")
            return None
