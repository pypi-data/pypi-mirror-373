from __future__ import annotations
import numpy as np
from typing import List, Dict, Any, Tuple


class MultiAssetEnv:
    """
    Multi-asset market-making environment.
    - M assets with correlated OU mid-prices
    - For each asset, K depth levels on each side
    - Agent provides per-asset quote prices and sizes for each level
    - Size-aware fill probability; maker fee/rebate applied on fills
    """

    def __init__(
        self,
        num_assets: int = 2,
        depth_levels: int = 3,
        tick_size: float = 0.01,
        seed: int | None = None,
        market: Dict[str, Any] | None = None,
        execution: Dict[str, Any] | None = None,
        fees: Dict[str, Any] | None = None,
    ) -> None:
        self.rng = np.random.default_rng(seed)
        self.num_assets = int(num_assets)
        self.depth_levels = int(depth_levels)
        self.tick_size = float(tick_size)

        market = market or {}
        ou = market.get("ou", {})
        self.mu = float(ou.get("mu", 100.0))
        self.kappa = float(ou.get("kappa", 0.05))
        self.dt = float(ou.get("dt", 1.0))
        self.sigma_vec = np.array(ou.get("sigma_vec", [0.5] * self.num_assets), dtype=float)
        # Correlation matrix
        corr = np.array(market.get("correlation", np.eye(self.num_assets)), dtype=float)
        # Cholesky for generating correlated noise
        self.chol = np.linalg.cholesky(corr + 1e-12 * np.eye(self.num_assets))

        self.vol_regime = market.get("vol_regime", {"enabled": True, "high_sigma_scale": 3.0, "switch_prob": 0.02})
        self._sigma_scale = np.ones(self.num_assets)

        execution = execution or {}
        self.base_rate = float(execution.get("base_arrival_rate", 1.0))
        self.alpha = float(execution.get("alpha", 1.5))
        self.size_sensitivity = float(execution.get("size_sensitivity", 0.1))

        fees = fees or {}
        self.maker_fee_bps = float(fees.get("maker_bps", -0.5))  # rebate default (-)
        self.taker_fee_bps = float(fees.get("taker_bps", 1.0))

        self.mid = np.full(self.num_assets, self.mu, dtype=float)
        self.inventory = np.zeros(self.num_assets, dtype=int)
        self.pnl = 0.0
        self.time = 0
        self.history: List[Dict[str, Any]] = []

    def reset(self) -> None:
        self.mid[:] = self.mu
        self.inventory[:] = 0
        self.pnl = 0.0
        self.time = 0
        self.history = []
        self._sigma_scale[:] = 1.0

    def _update_regime(self) -> None:
        if self.vol_regime.get("enabled", False):
            if self.rng.random() < float(self.vol_regime.get("switch_prob", 0.02)):
                # Flip regime scale between 1.0 and high
                high = float(self.vol_regime.get("high_sigma_scale", 3.0))
                self._sigma_scale = np.where(self._sigma_scale == 1.0, high, 1.0)

    def _update_mid(self) -> None:
        # correlated Gaussian noise
        z = self.rng.normal(0.0, 1.0, size=self.num_assets)
        corr_noise = self.chol @ z
        sigma = self.sigma_vec * self._sigma_scale
        dS = self.kappa * (self.mu - self.mid) * self.dt + sigma * np.sqrt(self.dt) * corr_noise
        self.mid = self.mid + dS

    def _p_fill(self, quote_px: float, mid: float, size: float) -> float:
        # Distance decay and size penalty
        dist_ticks = max(0.0, abs(quote_px - mid) / self.tick_size)
        lam = self.base_rate * np.exp(-self.alpha * dist_ticks) * np.exp(-self.size_sensitivity * max(0.0, size))
        return float(np.clip(1.0 - np.exp(-lam), 0.0, 1.0))

    def _apply_maker_fee(self, price: float, side: str) -> float:
        fee = price * (self.maker_fee_bps / 1e4)
        return price + fee if side == "buy" else price - fee

    def step(
        self,
        bids: List[List[Tuple[float, float]]],
        asks: List[List[Tuple[float, float]]],
    ) -> Dict[str, Any]:
        """
        bids, asks: list for each asset of length depth_levels; each entry is (price, size)
        Maker fills: if external order hits our quotes with probability depending on distance and size.
        This env is passive; taker fees would apply if we modeled active crossing.
        """
        executed = {"bids": [[None] * self.depth_levels for _ in range(self.num_assets)],
                    "asks": [[None] * self.depth_levels for _ in range(self.num_assets)]}
        # Iterate assets and levels
        for a in range(self.num_assets):
            for k in range(self.depth_levels):
                # Ask fill (we sell): maker
                ask_px, ask_sz = asks[a][k]
                p_ask = self._p_fill(ask_px, self.mid[a], ask_sz)
                if self.rng.random() < p_ask and ask_sz > 0:
                    eff_px = self._apply_maker_fee(ask_px, side="sell")
                    self.inventory[a] -= int(ask_sz)
                    self.pnl += eff_px * float(ask_sz)
                    executed["asks"][a][k] = eff_px
                # Bid fill (we buy): maker
                bid_px, bid_sz = bids[a][k]
                p_bid = self._p_fill(bid_px, self.mid[a], bid_sz)
                if self.rng.random() < p_bid and bid_sz > 0:
                    eff_px = self._apply_maker_fee(bid_px, side="buy")
                    self.inventory[a] += int(bid_sz)
                    self.pnl -= eff_px * float(bid_sz)
                    executed["bids"][a][k] = eff_px

        self._update_regime()
        self._update_mid()
        self.time += 1
        rec = {
            "time": self.time,
            "mid": self.mid.copy(),
            "inventory": self.inventory.copy(),
            "pnl": self.pnl,
            "sigma_scale": self._sigma_scale.copy(),
            "executed": executed,
        }
        self.history.append(rec)
        return rec