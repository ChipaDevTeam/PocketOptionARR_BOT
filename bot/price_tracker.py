import asyncio
from BinaryOptionsToolsV2.pocketoption import PocketOptionAsync


class PriceTracker:
    """Subscribes to symbols and exposes their latest prices."""

    def __init__(self):
        self._prices: dict[str, float | None] = {}
        self._callbacks: list = []

    @property
    def prices(self) -> dict[str, float | None]:
        return dict(self._prices)

    def get(self, symbol: str) -> float | None:
        return self._prices.get(symbol)

    def on_update(self, callback):
        """Register a callback(symbol, price) fired on every tick."""
        self._callbacks.append(callback)

    async def watch(self, api: PocketOptionAsync, symbol: str):
        """Subscribe to *symbol* and keep its price up to date forever."""
        self._prices.setdefault(symbol, None)
        stream = await api.subscribe_symbol(symbol)
        async for candle in stream:
            price = float(candle["close"])
            self._prices[symbol] = price
            for cb in self._callbacks:
                cb(symbol, price)

    async def wait_for_prices(self, *symbols: str, poll: float = 0.25):
        """Block until all requested symbols have at least one price."""
        while any(self._prices.get(s) is None for s in symbols):
            await asyncio.sleep(poll)
