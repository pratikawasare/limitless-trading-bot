from typing import List, Tuple, Dict

from config import Config
from market_discovery import MarketInfo
from position_manager import PositionManager
from limitless_client import LimitlessClient


class ExecutionEngine:
    def __init__(self, config: Config, logger, client: LimitlessClient, position_manager: PositionManager):
        self._config = config
        self._logger = logger
        self._client = client
        self._positions = position_manager

    async def execute_entries(self, entries: List[Tuple[MarketInfo, float, float]]):
        for market, edge, size in entries:
            if self._positions.has_position(market.market_id):
                continue

            self._logger.info(
                f"ENTRY signal: market={market.market_id} title='{market.title}' edge={edge:.4f} size={size:.4f}"
            )

            if self._config.paper_trading:
                self._logger.info(
                    f"[PAPER] Simulating buy_yes: market={market.market_id} size={size:.4f}"
                )
                self._positions.open_position(market, size, market.yes_price)
                continue

            order = await self._client.buy_yes(market.market_id, size)
            if order is not None:
                self._positions.open_position(market, size, market.yes_price)
                self._logger.info(f"Live buy_yes order executed: {order}")
            else:
                self._logger.error(f"Live buy_yes order failed for market {market.market_id}")

    async def execute_exits(self, markets: List[MarketInfo], edges_by_market: dict):
        for m in markets:
            pos = self._positions.get_position(m.market_id)
            if not pos:
                continue
            current_edge = edges_by_market.get(m.market_id, 0.0)
            exit_pos = self._positions.evaluate_exit(m, m.yes_price, current_edge)
            if not exit_pos:
                continue

            self._logger.info(
                f"EXIT signal: market={m.market_id} size={exit_pos.size:.4f}"
            )

            if self._config.paper_trading:
                self._logger.info(
                    f"[PAPER] Simulating sell_yes: market={m.market_id} size={exit_pos.size:.4f}"
                )
                self._positions.close_position(m.market_id)
                continue

            order = await self._client.sell_yes(m.market_id, exit_pos.size)
            if order is not None:
                self._positions.close_position(m.market_id)
                self._logger.info(f"Live sell_yes order executed: {order}")
            else:
                self._logger.error(f"Live sell_yes order failed for market {m.market_id}")
