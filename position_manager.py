import time
from dataclasses import dataclass
from typing import Dict, Optional

from config import Config
from market_discovery import MarketInfo


@dataclass
class Position:
    market_id: str
    entry_price: float
    size: float
    entry_time: float


class PositionManager:
    def __init__(self, config: Config, logger):
        self._config = config
        self._logger = logger
        self._positions: Dict[str, Position] = {}

    def has_position(self, market_id: str) -> bool:
        return market_id in self._positions

    def open_position(self, market: MarketInfo, size: float, entry_price: float):
        if self.has_position(market.market_id):
            self._logger.info(f"Position already open in {market.market_id}, skipping")
            return
        pos = Position(
            market_id=market.market_id,
            entry_price=entry_price,
            size=size,
            entry_time=time.time(),
        )
        self._positions[market.market_id] = pos
        self._logger.info(
            f"Opened position: market={market.market_id} size={size:.4f} entry_price={entry_price:.4f}"
        )

    def get_position(self, market_id: str) -> Optional[Position]:
        return self._positions.get(market_id)

    def close_position(self, market_id: str):
        if market_id in self._positions:
            pos = self._positions.pop(market_id)
            self._logger.info(
                f"Closed position: market={market_id} size={pos.size:.4f} entry_price={pos.entry_price:.4f}"
            )

    def evaluate_exit(self, market: MarketInfo, current_yes_price: float, current_edge: float) -> Optional[Position]:
        pos = self.get_position(market.market_id)
        if not pos:
            return None

        target_profit = self._config.take_profit_percent
        price_change = (current_yes_price - pos.entry_price) / pos.entry_price

        if price_change >= target_profit:
            self._logger.info(
                f"Take profit hit for {market.market_id}: change={price_change:.4f} >= {target_profit:.4f}"
            )
            return pos

        if current_edge < 0:
            self._logger.info(
                f"Opposite edge detected for {market.market_id}: edge={current_edge:.4f}"
            )
            return pos

        return None
