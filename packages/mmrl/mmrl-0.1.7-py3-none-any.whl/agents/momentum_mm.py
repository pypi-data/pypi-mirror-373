from __future__ import annotations
from dataclasses import dataclass, field
from collections import deque


@dataclass
class MomentumMarketMaker:
    spread: float = 0.12
    window: int = 20
    bias: float = 0.05  # skew factor towards momentum direction
    _prices: deque = field(default_factory=lambda: deque(maxlen=20))

    def _signal(self) -> float:
        if len(self._prices) < 2:
            return 0.0
        return float(self._prices[-1] - self._prices[0])

    def quote(self, mid_price: float, inventory: int):
        # Update history
        if self._prices.maxlen != self.window:
            self._prices = deque(self._prices, maxlen=self.window)
        self._prices.append(mid_price)
        sig = self._signal()
        skew = self.bias if sig > 0 else (-self.bias if sig < 0 else 0.0)
        half = self.spread / 2.0
        bid = mid_price - half - skew
        ask = mid_price + half - skew
        if ask <= bid:
            ask = bid + self.spread
        return bid, ask

