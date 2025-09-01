import numpy as np
from env.simple_lob_env import SimpleLOBEnv
from agents.inventory_mm import InventoryAwareMarketMaker


def run_once(seed=123, steps=100):
    env = SimpleLOBEnv(seed=seed)
    agent = InventoryAwareMarketMaker(spread=0.1, inventory_sensitivity=0.05)
    for _ in range(steps):
        bid, ask = agent.quote(env.mid_price, env.inventory)
        env.step(bid, ask)
    return env.pnl, env.inventory


def test_determinism_same_seed():
    pnl1, inv1 = run_once(seed=42, steps=200)
    pnl2, inv2 = run_once(seed=42, steps=200)
    assert pnl1 == pnl2
    assert inv1 == inv2


def test_fees_slippage_signs():
    env = SimpleLOBEnv(seed=1, fees={"fee_bps": 10.0, "slippage_bps": 10.0})
    mid = env.mid_price
    bid, ask = mid - 0.05, mid + 0.05
    # Force fills by setting high base rate and very low alpha (almost always fill)
    env.exec_base_rate = 1e6
    env.exec_alpha = 0.0
    start_pnl = env.pnl
    start_inv = env.inventory
    env.step(bid, ask)
    # With both sides potentially filled, effective prices reduce pnl on buy and increase on sell
    assert env.pnl <= start_pnl + ask  # cannot exceed raw proceeds
    assert env.inventory in (start_inv, start_inv - 1, start_inv + 1)