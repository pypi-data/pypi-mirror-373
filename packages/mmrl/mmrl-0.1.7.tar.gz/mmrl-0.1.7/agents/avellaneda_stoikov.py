import math


class AvellanedaStoikovMM:
    def __init__(self, risk_aversion: float = 0.1, base_spread: float = 0.1, inv_penalty: float = 0.05):
        self.risk_aversion = risk_aversion
        self.base_spread = base_spread
        self.inv_penalty = inv_penalty

    def quote(self, mid_price: float, inventory: int, sigma: float = 0.5):
        # Simplified AS: skew proportional to inventory and risk aversion
        skew = self.risk_aversion * inventory * max(sigma, 1e-6)
        optimal_spread = self.base_spread + self.inv_penalty * abs(inventory)
        half = optimal_spread / 2.0
        bid = mid_price - half + skew
        ask = mid_price + half + skew
        # Ensure bid < ask
        if ask <= bid:
            ask = bid + optimal_spread
        return bid, ask