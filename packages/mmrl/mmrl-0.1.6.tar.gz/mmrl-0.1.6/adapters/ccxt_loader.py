from __future__ import annotations
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

import ccxt
import pandas as pd


def fetch_trades_to_parquet(exchange_id: str, symbol: str, limit: int = 500, out_path: str = 'data/trades.parquet', since: Optional[int] = None, max_pages: int = 10) -> str:
    """Fetch recent trades via CCXT and write to a Parquet file.

    Creates the destination directory if needed.
    """
    ex = getattr(ccxt, exchange_id)()
    trades = _fetch_all_trades(ex, symbol, since=since, limit=limit, max_pages=max_pages)
    df = pd.DataFrame(trades)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)
    return str(out)


def _fetch_all_trades(ex, symbol: str, since: Optional[int] = None, limit: int = 1000, max_pages: int = 100) -> List[Dict[str, Any]]:
    """Paginate and retry to fetch trades."""
    all_trades: List[Dict[str, Any]] = []
    params = {}
    retries = 0
    last_id = None
    for _ in range(max_pages):
        try:
            batch = ex.fetch_trades(symbol, since=since, limit=limit, params=params)
            if not batch:
                break
            all_trades.extend(batch)
            last_id = batch[-1].get('id')
            since = batch[-1].get('timestamp') or since
        except Exception:
            retries += 1
            if retries > 5:
                break
            ex.sleep(1000 * retries)
            continue
    return all_trades


def csv_to_vectorbt_signals(csv_path: str) -> pd.DataFrame:
    """Convert a run CSV (inventory_mm_run.csv) to a basic vectorbt signals frame.

    Returns a DataFrame with 'close', 'entries', 'exits' columns for quick vectorbt demo.
    """
    df = pd.read_csv(csv_path)
    # Use mid_price as close proxy
    out = pd.DataFrame()
    out['close'] = df['mid_price'].astype(float)
    # Define naive entries/exits from inventory changes
    inv = df['inventory'].astype(float).fillna(0)
    delta = inv.diff().fillna(0)
    out['entries'] = (delta > 0).astype(bool)
    out['exits'] = (delta < 0).astype(bool)
    return out