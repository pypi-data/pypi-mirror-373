from __future__ import annotations
from dataclasses import dataclass


@dataclass
class MeanReversionMarketMaker:
    target_spread: float = 0.1
    kappa: float = 0.1  # inventory mean reversion strength
    skew_sensitivity: float = 0.05

    def quote(self, mid_price: float, inventory: int):
        # Mean-revert inventory to 0 by skewing quotes
        skew = -self.kappa * inventory * self.skew_sensitivity
        half = self.target_spread / 2.0
        bid = mid_price - half + skew
        ask = mid_price + half + skew
        if ask <= bid:
            ask = bid + self.target_spread
        return bid, ask

