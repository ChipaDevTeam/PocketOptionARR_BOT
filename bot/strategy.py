from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class Signal(Enum):
    CALL = "CALL"
    PUT = "PUT"
    NONE = "NONE"


@dataclass(frozen=True)
class GapSignal:
    signal: Signal
    gap: float
    real_price: float
    otc_price: float


class GapStrategy:
    """Decides whether to trade based on the price gap."""

    def __init__(self, threshold: float):
        self.threshold = threshold

    def evaluate(self, real_price: float, otc_price: float) -> GapSignal:
        gap = real_price - otc_price

        if gap >= self.threshold:
            return GapSignal(Signal.CALL, gap, real_price, otc_price)
        elif gap <= -self.threshold:
            return GapSignal(Signal.PUT, gap, real_price, otc_price)
        else:
            return GapSignal(Signal.NONE, gap, real_price, otc_price)
