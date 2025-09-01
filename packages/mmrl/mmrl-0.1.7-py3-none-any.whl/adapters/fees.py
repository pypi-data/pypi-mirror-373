from __future__ import annotations
from dataclasses import dataclass


@dataclass
class FeeSchedule:
    maker_bps: float = -0.5  # rebate
    taker_bps: float = 1.0

    def maker_price(self, px: float, side: str) -> float:
        fee = px * (self.maker_bps / 1e4)
        return px + fee if side == 'buy' else px - fee

    def taker_price(self, px: float, side: str) -> float:
        fee = px * (self.taker_bps / 1e4)
        return px + fee if side == 'buy' else px - fee