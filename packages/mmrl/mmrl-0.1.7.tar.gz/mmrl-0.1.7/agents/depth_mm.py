from __future__ import annotations
from typing import List, Tuple
import numpy as np


class DepthAwareMarketMaker:
    def __init__(
        self,
        depth_levels: int = 3,
        base_spread: float = 0.1,
        level_widen: float = 0.05,
        base_size: float = 1.0,
        inv_sensitivity: float = 0.02,
        regime_skew: float = 0.05,
    ) -> None:
        self.depth_levels = depth_levels
        self.base_spread = base_spread
        self.level_widen = level_widen
        self.base_size = base_size
        self.inv_sensitivity = inv_sensitivity
        self.regime_skew = regime_skew

    def quote_asset(self, mid: float, inventory: int, sigma_scale: float) -> Tuple[List[Tuple[float, float]], List[Tuple[float, float]]]:
        """
        Returns (bids, asks) for one asset, each as list[(price, size)] over depth_levels.
        Regime-conditioned widening/skew:
        - Higher sigma_scale widens spreads and reduces size.
        - Inventory skews quotes to encourage rebalancing.
        """
        bids: List[Tuple[float, float]] = []
        asks: List[Tuple[float, float]] = []
        inv_skew = self.inv_sensitivity * inventory
        for k in range(self.depth_levels):
            widen = self.level_widen * k
            spread_k = self.base_spread * (1.0 + self.regime_skew * (sigma_scale - 1.0)) + widen
            half = spread_k / 2.0
            size_k = max(0.1, self.base_size / (1.0 + 0.5 * k) / max(1.0, sigma_scale))
            bid = mid - half + inv_skew
            ask = mid + half + inv_skew
            # Ensure ordering
            if ask <= bid:
                ask = bid + spread_k
            bids.append((bid, size_k))
            asks.append((ask, size_k))
        return bids, asks

    def quote(self, mids: np.ndarray, inventory: np.ndarray, sigma_scales: np.ndarray) -> Tuple[List[List[Tuple[float, float]]], List[List[Tuple[float, float]]]]:
        all_bids = []
        all_asks = []
        for a in range(len(mids)):
            b, a_ = self.quote_asset(float(mids[a]), int(inventory[a]), float(sigma_scales[a]))
            all_bids.append(b)
            all_asks.append(a_)
        return all_bids, all_asks