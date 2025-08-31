from __future__ import annotations

from pathlib import Path
from typing import Tuple, Dict, Any

from experiments.run_inventory_mm import run_backtest as _run_backtest

__all__ = ["run_backtest", "__version__"]
__version__ = "0.1.2"


def run_backtest(config: Dict[str, Any]) -> Tuple[Path, Dict[str, Any]]:
    """Programmatic API: run a backtest and return (run_dir, metrics)."""
    return _run_backtest(config)

