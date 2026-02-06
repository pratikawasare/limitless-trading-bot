import asyncio
import signal
from typing import Dict

from config import load_config
from logger import setup_logger
from limitless_client import LimitlessClient
from binance_feed import BinancePriceFeed
from market_discovery import MarketDiscovery
from risk_manager import RiskManager
from position_manager import PositionManager
from strategy import StrategyEngine
from execution import ExecutionEngine


class LimitlessBot:
    def __init__(self):
        self._config = load_config()
        self._logger = setup_logger(self._config)

        self._client = LimitlessClient(self._config, self._logger)
        self._binance_feed = BinancePriceFeed(self._logger)
        self._market_discovery = MarketDiscovery(self._client, self._config, self._logger)
        self._risk_manager = RiskManager(self._config, self._logger)
        self._position_manager = PositionManager(self._config, self._logger)
        self._strategy = StrategyEngine(
            self._config,
            self._logger,
            self._risk_manager,
            self._position_manager,
            self._client,
        )
        self._execution = ExecutionEngine(
            self._config,
            self._logger,
            self._client,
            self._position_manager,
        )

        self._should_stop = asyncio.Event()

    async def _start_binance_feed(self):
        await self._binance_feed.start()

    async def _periodic_market_refresh(self):
        while not self._should_stop.is_set():
            try:
                await self._market_discovery.refresh_markets()
            except Exception as e:
                self._logger.error(f"Error during market refresh: {e}")
            await asyncio.sleep(self._config.market_refresh_interval)

    async def _main_loop(self):
        self._logger.info("Starting main trading loop")
        while not self._should_stop.is_set():
            try:
                btc_price = await self._binance_feed.get_price()
                markets = await self._market_discovery.get_markets()
                balance = await self._client.get_balance()

                entries = await self._strategy.scan_markets(btc_price, markets, balance)

                edges_by_market: Dict[str, float] = {}
                if btc_price is not None:
                    for m in markets:
                        real_prob = (
                            0.0 if m.target_price <= 0 else min(max(btc_price / m.target_price, 0.0), 1.0)
                        )
                        edge = real_prob - m.yes_price
                        edges_by_market[m.market_id] = edge

                await self._execution.execute_entries(entries)
                await self._execution.execute_exits(markets, edges_by_market)
            except Exception as e:
                self._logger.error(f"Error in main loop: {e}")

            await asyncio.sleep(self._config.main_loop_sleep)

        self._logger.info("Main trading loop stopped")

    async def run(self):
        loop = asyncio.get_running_loop()

        def _handle_signal():
            self._logger.info("Shutdown signal received")
            self._should_stop.set()

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, _handle_signal)
            except NotImplementedError:
                pass

        feed_task = asyncio.create_task(self._start_binance_feed(), name="binance_feed")
        discovery_task = asyncio.create_task(self._periodic_market_refresh(), name="market_refresh")
        main_loop_task = asyncio.create_task(self._main_loop(), name="main_loop")

        await self._should_stop.wait()

        self._logger.info("Stopping tasks...")
        await self._binance_feed.stop()
        for task in (feed_task, discovery_task, main_loop_task):
            task.cancel()
        await asyncio.gather(feed_task, discovery_task, main_loop_task, return_exceptions=True)
        self._logger.info("Bot shutdown complete")


def main():
    asyncio.run(LimitlessBot().run())


if __name__ == "__main__":
    main()
