from __future__ import annotations

import importlib
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Iterable, List, Tuple

import json
import pandas as pd
import matplotlib.pyplot as plt

from env.simple_lob_env import SimpleLOBEnv
from utils.metrics import sharpe, max_drawdown, hit_rate


def _load_builtin_agent(name: str, cfg: Dict[str, Any]):
    key = name.lower()
    if key in ("naive",):
        from agents.naive_mm import NaiveMarketMaker
        return NaiveMarketMaker(spread=cfg.get("agent", {}).get("spread", 0.1))
    if key in ("inventory", "inventory_aware"):
        from agents.inventory_mm import InventoryAwareMarketMaker
        a = cfg.get("agent", {})
        return InventoryAwareMarketMaker(spread=a.get("spread", 0.1), inventory_sensitivity=a.get("inventory_sensitivity", 0.05))
    if key in ("avellaneda", "as", "avellaneda_stoikov"):
        from agents.avellaneda_stoikov import AvellanedaStoikovMM
        a = cfg.get("avellaneda", {"risk_aversion": 0.1, "base_spread": 0.1, "inv_penalty": 0.05})
        return AvellanedaStoikovMM(**a)
    if key in ("depth",):
        from agents.depth_mm import DepthAwareMarketMaker
        return DepthAwareMarketMaker()
    if key in ("meanrev", "mean_reversion"):
        from agents.mean_reversion_mm import MeanReversionMarketMaker
        return MeanReversionMarketMaker()
    if key in ("momentum",):
        from agents.momentum_mm import MomentumMarketMaker
        return MomentumMarketMaker()
    raise ValueError(f"Unknown built-in agent '{name}'")


def _load_agent(spec: str, cfg: Dict[str, Any]):
    """Load agent from built-in name or dotted path 'module:Class'."""
    if ":" in spec:
        mod_name, cls_name = spec.split(":", 1)
        mod = importlib.import_module(mod_name)
        cls = getattr(mod, cls_name)
        return cls(**cfg.get("agent", {}))
    return _load_builtin_agent(spec, cfg)


@dataclass
class BenchmarkResult:
    out_dir: Path
    metrics_csv: Path
    plot_path: Path | None


def run_benchmark(agent_specs: Iterable[str], cfg: Dict[str, Any], steps: int, out_dir: Path, make_plot: bool = True) -> BenchmarkResult:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows: List[Dict[str, Any]] = []
    for spec in agent_specs:
        env = SimpleLOBEnv(seed=cfg.get("seed"), market=cfg.get("market"), execution=cfg.get("execution"), fees=cfg.get("fees"))
        agent = _load_agent(spec, cfg)
        for _ in range(steps):
            bid, ask = agent.quote(env.mid_price, env.inventory)
            env.step(bid, ask)

        df = pd.DataFrame(env.history)
        returns = df["pnl"].diff().fillna(0.0).values
        rows.append({
            "agent": spec,
            "final_pnl": float(df["pnl"].iloc[-1]) if not df.empty else 0.0,
            "sharpe": sharpe(returns) if len(returns) > 0 else 0.0,
            "max_drawdown": max_drawdown(df["pnl"].values) if not df.empty else 0.0,
            "hit_rate": hit_rate(returns) if len(returns) > 0 else 0.0,
        })

    metrics_df = pd.DataFrame(rows)
    metrics_csv = out_dir / "benchmark_metrics.csv"
    metrics_df.to_csv(metrics_csv, index=False)

    plot_path: Path | None = None
    if make_plot and not metrics_df.empty:
        fig, ax = plt.subplots(1, 1, figsize=(10, 4))
        metrics_df.sort_values("sharpe", ascending=False, inplace=True)
        ax.bar(metrics_df["agent"], metrics_df["sharpe"], color="#2c7fb8")
        ax.set_title("Sharpe ratio by agent")
        ax.set_ylabel("Sharpe")
        ax.grid(True, axis="y", alpha=0.3)
        plt.xticks(rotation=20, ha="right")
        plot_path = out_dir / "benchmark_sharpe.png"
        fig.tight_layout()
        fig.savefig(plot_path, dpi=160)
        plt.close(fig)

    return BenchmarkResult(out_dir=out_dir, metrics_csv=metrics_csv, plot_path=plot_path)

