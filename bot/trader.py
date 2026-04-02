from __future__ import annotations
import asyncio
from BinaryOptionsToolsV2.pocketoption import PocketOptionAsync
from bot.strategy import GapSignal, Signal
from bot.stats import TradeLogger


class Trader:
    """Places trades and tracks results."""

    def __init__(
        self,
        api: PocketOptionAsync,
        otc_asset: str,
        amount: float,
        duration: int,
        cooldown: float,
        logger: TradeLogger,
    ):
        self._api = api
        self._otc_asset = otc_asset
        self._amount = amount
        self._duration = duration
        self._cooldown = cooldown
        self._logger = logger
        self._last_trade_time: float = 0.0

    def _now(self) -> float:
        return asyncio.get_event_loop().time()

    @property
    def on_cooldown(self) -> bool:
        return (self._now() - self._last_trade_time) < self._cooldown

    async def execute(self, signal: GapSignal):
        """Place a trade based on the signal. Returns immediately; result
        is tracked in the background."""
        if signal.signal is Signal.NONE:
            return
        if self.on_cooldown:
            return

        self._last_trade_time = self._now()
        direction = signal.signal.value

        try:
            if signal.signal is Signal.CALL:
                trade_id, data = await self._api.buy(
                    asset=self._otc_asset,
                    amount=self._amount,
                    time=self._duration,
                    check_win=False,
                )
            else:
                trade_id, data = await self._api.sell(
                    asset=self._otc_asset,
                    amount=self._amount,
                    time=self._duration,
                    check_win=False,
                )

            print(f"\n[TRADE] {direction} | gap {signal.gap:+.5f} | ID {trade_id}")
            asyncio.create_task(self._track_result(trade_id, signal))

        except Exception as e:
            print(f"\n[ERR]   Failed {direction}: {e}")

    async def _track_result(self, trade_id: str, signal: GapSignal):
        try:
            result = await self._api.check_win(trade_id)
            outcome = result.get("result", "unknown")
            print(
                f"\n[RESULT] {signal.signal.value} (gap {signal.gap:+.5f}) "
                f"→ {outcome.upper()}"
            )
            self._logger.record(
                trade_id=trade_id,
                direction=signal.signal.value,
                gap=signal.gap,
                real_price=signal.real_price,
                otc_price=signal.otc_price,
                outcome=outcome,
                amount=self._amount,
                duration=self._duration,
            )
        except Exception as e:
            print(f"\n[ERR]   Could not check {trade_id}: {e}")
