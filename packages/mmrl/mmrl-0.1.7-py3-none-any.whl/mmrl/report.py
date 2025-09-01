from __future__ import annotations

import base64
import io
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

import numpy as np
import pandas as pd

from utils.metrics import calculate_all_metrics


def _encode_fig_as_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=160)
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def _find_csv_in_run_dir(run_dir: Path) -> Optional[Path]:
    candidates = [
        run_dir / "inventory_mm_run.csv",
        run_dir / "stream_run.csv",
    ]
    for c in candidates:
        if c.exists():
            return c
    # fallback: any csv
    for p in run_dir.glob("*.csv"):
        return p
    return None


def generate_report(run_dir_or_csv: str, output_html: Optional[str] = None) -> Path:
    """Generate a self-contained HTML report with plots and metrics.

    - Accepts either a run directory or a CSV file path
    - Produces an inline-asset HTML (single file)
    """
    import matplotlib.pyplot as plt  # lazy import

    p = Path(run_dir_or_csv)
    if p.is_dir():
        csv_path = _find_csv_in_run_dir(p)
        if csv_path is None:
            raise FileNotFoundError(f"No CSV found in {p}")
        run_dir = p
    else:
        csv_path = p
        run_dir = p.parent

    df = pd.read_csv(csv_path)
    if "pnl" not in df.columns:
        # compute pnl if prices present? keep simple: require column
        df["pnl"] = 0.0

    returns = df["pnl"].diff().fillna(0.0).to_numpy()
    metrics = calculate_all_metrics(returns)

    # Plots
    figs: Dict[str, str] = {}

    # PnL and inventory
    fig, ax = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    ax[0].plot(df.get("pnl", pd.Series(dtype=float)), label="PnL", color="#2c7fb8")
    ax[0].set_title("PnL over time")
    ax[0].grid(True, alpha=0.3)
    if "inventory" in df.columns:
        ax[1].plot(df["inventory"], label="Inventory", color="#31a354")
        ax[1].set_title("Inventory over time")
        ax[1].grid(True, alpha=0.3)
    else:
        ax[1].axis("off")
    figs["equity_inventory"] = _encode_fig_as_base64(fig)
    plt.close(fig)

    # Mid-price
    if "mid_price" in df.columns:
        fig, ax = plt.subplots(1, 1, figsize=(10, 3))
        ax.plot(df["mid_price"], color="#636363")
        ax.set_title("Mid-price")
        ax.grid(True, alpha=0.3)
        figs["mid_price"] = _encode_fig_as_base64(fig)
        plt.close(fig)

    # Rolling Sharpe (simple window)
    if len(returns) > 10:
        window = max(20, min(252, len(returns) // 5))
        rolling = pd.Series(returns).rolling(window).apply(
            lambda x: (np.mean(x) / (np.std(x) + 1e-12)) * np.sqrt(252), raw=True
        )
        fig, ax = plt.subplots(1, 1, figsize=(10, 3))
        ax.plot(rolling.values, color="#e6550d")
        ax.axhline(0, color="black", alpha=0.3)
        ax.set_title(f"Rolling Sharpe (window={window})")
        ax.grid(True, alpha=0.3)
        figs["rolling_sharpe"] = _encode_fig_as_base64(fig)
        plt.close(fig)

    # Build HTML
    mjson = json.dumps(metrics, indent=2)
    html = f"""
    <html>
    <head>
      <meta charset='utf-8'/>
      <title>MMRL Report</title>
      <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif; margin: 24px; }}
        .grid {{ display: grid; grid-template-columns: 1fr; gap: 16px; }}
        pre {{ background: #f6f8fa; padding: 12px; border-radius: 6px; overflow-x: auto; }}
        img {{ max-width: 100%; height: auto; border: 1px solid #eee; border-radius: 6px; }}
        h1, h2 {{ margin: 8px 0; }}
      </style>
    </head>
    <body>
      <h1>MMRL Report</h1>
      <p>Source: {csv_path}</p>
      <h2>Metrics</h2>
      <pre>{mjson}</pre>
      <div class='grid'>
        <div><img src='{figs.get("equity_inventory", "")}' alt='PnL and Inventory'/></div>
        {f"<div><img src='{figs.get('mid_price','')}' alt='Mid-price'/></div>" if 'mid_price' in figs else ''}
        {f"<div><img src='{figs.get('rolling_sharpe','')}' alt='Rolling Sharpe'/></div>" if 'rolling_sharpe' in figs else ''}
      </div>
    </body>
    </html>
    """

    out_path = Path(output_html) if output_html else (run_dir / "report.html")
    out_path.write_text(html)
    return out_path

