import numpy as np


class SimpleLOBEnv:
    def __init__(self, mid_price=100.0, tick_size=0.01, max_inventory=10, seed: int | None = None,
                 market: dict | None = None, execution: dict | None = None, fees: dict | None = None):
        self.rng = np.random.default_rng(seed)

        # Core state
        self.tick_size = float(tick_size)
        self.max_inventory = int(max_inventory)
        self.time = 0
        self.inventory = 0
        self.pnl = 0.0
        self.history = []

        # Market model config
        market = market or {}
        ou_cfg = (market.get('ou') or {})
        self.ou_enabled = bool(market.get('ou_enabled', True))
        self.ou_mu = float(ou_cfg.get('mu', mid_price))
        self.ou_kappa = float(ou_cfg.get('kappa', 0.05))
        self.ou_sigma = float(ou_cfg.get('sigma', 0.5))
        self.ou_dt = float(ou_cfg.get('dt', 1.0))

        vr = (market.get('vol_regime') or {})
        self.vr_enabled = bool(vr.get('enabled', False))
        self.vr_high_sigma = float(vr.get('high_sigma', self.ou_sigma * 2.0))
        self.vr_switch_prob = float(vr.get('switch_prob', 0.0))
        self._current_sigma = self.ou_sigma

        # Execution model
        execution = execution or {}
        self.exec_base_rate = float(execution.get('base_arrival_rate', 1.0))
        self.exec_alpha = float(execution.get('alpha', 1.5))

        # Fees/slippage
        fees = fees or {}
        self.fee_bps = float(fees.get('fee_bps', 0.0))
        self.slippage_bps = float(fees.get('slippage_bps', 0.0))

        # Initialize mid
        self.mid_price = float(self.ou_mu)

    def reset(self):
        self.time = 0
        self.inventory = 0
        self.pnl = 0.0
        self.history = []
        self._current_sigma = self.ou_sigma
        self.mid_price = float(self.ou_mu)

    def _update_vol_regime(self):
        if not self.vr_enabled:
            return
        if self.rng.random() < self.vr_switch_prob:
            self._current_sigma = self.vr_high_sigma if np.isclose(self._current_sigma, self.ou_sigma) else self.ou_sigma

    def _update_mid_price(self):
        if self.ou_enabled:
            noise = self.rng.normal(0.0, 1.0)
            dS = self.ou_kappa * (self.ou_mu - self.mid_price) * self.ou_dt + self._current_sigma * np.sqrt(self.ou_dt) * noise
            self.mid_price = float(self.mid_price + dS)
        else:
            self.mid_price += float(self.rng.uniform(-0.05, 0.05))

    def _fill_probability(self, quote_price: float, side: str) -> float:
        dist_ticks = max(0.0, abs(quote_price - self.mid_price) / self.tick_size)
        lam = self.exec_base_rate * np.exp(-self.exec_alpha * dist_ticks)
        p_fill = 1.0 - np.exp(-lam)
        return float(np.clip(p_fill, 0.0, 1.0))

    def _apply_fees_slippage(self, price: float, side: str) -> float:
        slip = price * (self.slippage_bps / 1e4)
        fee = price * (self.fee_bps / 1e4)
        if side == 'sell':
            effective = price - slip - fee
        else:
            effective = price + slip + fee
        return float(effective)

    def step(self, bid_quote: float, ask_quote: float):
        if ask_quote <= bid_quote:
            ask_quote = bid_quote + self.tick_size

        trade_executed_bid = False
        trade_executed_ask = False
        executed_price_bid = None
        executed_price_ask = None

        can_buy = (self.inventory < self.max_inventory)
        can_sell = (self.inventory > -self.max_inventory)

        if can_sell:
            p_ask = self._fill_probability(ask_quote, side='sell')
            if self.rng.random() < p_ask:
                trade_executed_ask = True
                px = self._apply_fees_slippage(ask_quote, 'sell')
                self.inventory -= 1
                self.pnl += px
                executed_price_ask = px

        if can_buy:
            p_bid = self._fill_probability(bid_quote, side='buy')
            if self.rng.random() < p_bid:
                trade_executed_bid = True
                px = self._apply_fees_slippage(bid_quote, 'buy')
                self.inventory += 1
                self.pnl -= px
                executed_price_bid = px

        self._update_vol_regime()
        self._update_mid_price()
        self.time += 1

        self.history.append({
            'time': self.time,
            'bid': bid_quote,
            'ask': ask_quote,
            'mid_price': self.mid_price,
            'inventory': self.inventory,
            'executed_bid': executed_price_bid,
            'executed_ask': executed_price_ask,
            'pnl': self.pnl,
            'sigma': self._current_sigma
        })

        return self.history[-1]
    
    # --- Data-driven stepping support ---
    def step_from_tick(self, tick: dict) -> dict:
        """Update env state from an external tick dict.

        Expected keys (optional, with fallbacks): time, mid_price, best_bid, best_ask.
        This does not simulate probabilistic fills; it just moves the reference state,
        so you can combine with your own execution logic if desired.
        """
        self.time = int(tick.get('time', self.time + 1))
        self.mid_price = float(tick.get('mid_price', self.mid_price))
        bid = float(tick.get('best_bid', self.mid_price - self.tick_size))
        ask = float(tick.get('best_ask', self.mid_price + self.tick_size))
        self.history.append({
            'time': self.time,
            'bid': bid,
            'ask': ask,
            'mid_price': self.mid_price,
            'inventory': self.inventory,
            'executed_bid': None,
            'executed_ask': None,
            'pnl': self.pnl,
            'sigma': self._current_sigma
        })
        return self.history[-1]
    


    
    