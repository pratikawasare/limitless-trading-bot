import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    limitless_api_key: str
    edge_threshold: float
    take_profit_percent: float
    paper_trading: bool
    max_position_percent: float
    log_level: str
    log_file: str
    market_refresh_interval: int = 60
    main_loop_sleep: float = 0.25


def _get_bool(env_name: str, default: bool) -> bool:
    val = os.getenv(env_name)
    if val is None:
        return default
    return val.lower() in ("1", "true", "yes", "on")


def load_config() -> Config:
    api_key = os.getenv("LIMITLESS_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("LIMITLESS_API_KEY is not set in environment")

    edge_threshold = float(os.getenv("EDGE_THRESHOLD", "0.05"))
    take_profit_percent = float(os.getenv("TAKE_PROFIT_PERCENT", "0.03"))
    paper_trading = _get_bool("PAPER_TRADING", True)
    max_position_percent = float(os.getenv("MAX_POSITION_PERCENT", "0.6"))
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_file = os.getenv("LOG_FILE", "limitless_bot.log")

    return Config(
        limitless_api_key=api_key,
        edge_threshold=edge_threshold,
        take_profit_percent=take_profit_percent,
        paper_trading=paper_trading,
        max_position_percent=max_position_percent,
        log_level=log_level,
        log_file=log_file,
    )
