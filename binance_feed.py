import asyncio
import json
import websockets
from typing import Optional


BINANCE_WS_URL = "wss://stream.binance.com:9443/ws/btcusdt@trade"


class BinancePriceFeed:
    def __init__(self, logger):
        self._logger = logger
        self._price: Optional[float] = None
        self._lock = asyncio.Lock()
        self._stop_event = asyncio.Event()

    async def start(self):
        while not self._stop_event.is_set():
            try:
                self._logger.info("Connecting to Binance websocket...")
                async with websockets.connect(BINANCE_WS_URL, ping_interval=20, ping_timeout=20) as ws:
                    self._logger.info("Connected to Binance websocket")
                    async for msg in ws:
                        if self._stop_event.is_set():
                            break
                        await self._handle_message(msg)
            except Exception as e:
                self._logger.error(f"Binance websocket error, reconnecting in 5s: {e}")
                await asyncio.sleep(5)

    async def _handle_message(self, msg: str):
        try:
            data = json.loads(msg)
            price_str = data.get("p") or data.get("price")
            if price_str is None:
                return
            price = float(price_str)
            async with self._lock:
                self._price = price
            self._logger.debug(f"Binance BTCUSDT price update: {price}")
        except Exception as e:
            self._logger.error(f"Error parsing Binance message: {e}")

    async def get_price(self) -> Optional[float]:
        async with self._lock:
            return self._price

    async def stop(self):
        self._stop_event.set()
