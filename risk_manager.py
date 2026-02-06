from config import Config


class RiskManager:
    def __init__(self, config: Config, logger):
        self._config = config
        self._logger = logger

    def get_position_size(self, balance: float, edge: float) -> float:
        if edge >= 0.10:
            pct = 0.60
        elif edge >= 0.07:
            pct = 0.40
        elif edge >= 0.05:
            pct = 0.20
        else:
            return 0.0

        pct = min(pct, self._config.max_position_percent)
        size = balance * pct
        self._logger.info(
            f"RiskManager sizing: edge={edge:.4f}, balance={balance:.4f}, pct={pct:.2f}, size={size:.4f}"
        )
        return max(size, 0.0)
