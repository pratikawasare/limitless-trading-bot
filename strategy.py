from typing import Optional, List, Tuple, Dict

from config import Config
from market_discovery import MarketInfo
from position_manager import PositionManager
from risk_manager import RiskManager
from limitless_client import LimitlessClient


class StrategyEngine:
    def __init__(self, config: Config, logger, risk_manager: RiskManager, position_manager: PositionManager, client: LimitlessClient):
        self._config = config
        self._logger = logger
        self._risk = risk_manager
        self._positions = position_manager
        self._client = client

    def _compute_real_probability(self, btc_price: float, target_price: float) -> float:
        if target_price <= 0:
            return 0.0
        p = btc_price / target_price
        if p < 0:
            p = 0.0
        if p > 1:
            p = 1.0
        return p

    def _compute_edge(self, real_prob: float, yes_price: float) -> float:
        return real_prob - yes_price

    async def scan_markets(self, btc_price: Optional[float], markets: List[MarketInfo], balance: float) -> List[Tuple[MarketInfo, float, float]]:
        if btc_price is None:
            self._logger.warning("No BTC price yet, skipping strategy scan")
            return []

        tradable: List[Tuple[MarketInfo, float, float]] = []
        for m in markets:
            real_prob = self._compute_real_probability(btc_price, m.target_price)
            edge = self._compute_edge(real_prob, m.yes_price)
            self._logger.debug(
                f"Market {m.market_id}: title='{m.title}' real_prob={real_prob:.4f} yes_price={m.yes_price:.4f} edge={edge:.4f}"
            )

            if edge < self._config.edge_threshold:
                continue
            if self._positions.has_position(m.market_id):
                self._logger.debug(f"Already in position for {m.market_id}, skipping entry")
                continue

            size = self._risk.get_position_size(balance, edge)
            if size <= 0:
                continue

            tradable.append((m, edge, size))

        return tradable
