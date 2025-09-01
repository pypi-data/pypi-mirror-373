from __future__ import annotations
from dataclasses import dataclass


@dataclass
class RiskConfig:
    max_inventory: int = 50
    max_drawdown: float = 0.2  # fraction
    halt_on_violation: bool = True


class RiskManager:
    def __init__(self, cfg: RiskConfig | None = None):
        self.cfg = cfg or RiskConfig()
        self.peak_pnl = 0.0
        self.halted = False

    def reset(self):
        self.peak_pnl = 0.0
        self.halted = False

    def check(self, inventory: int, pnl: float) -> bool:
        if self.halted:
            return False
        # Track peak PnL for drawdown
        if pnl > self.peak_pnl:
            self.peak_pnl = pnl
        dd = (self.peak_pnl - pnl) / self.peak_pnl if self.peak_pnl > 0 else 0.0
        inv_ok = abs(inventory) <= self.cfg.max_inventory
        dd_ok = dd <= self.cfg.max_drawdown
        ok = inv_ok and dd_ok
        if not ok and self.cfg.halt_on_violation:
            self.halted = True
        return ok