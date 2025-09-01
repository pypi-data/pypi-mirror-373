import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import yaml
import pandas as pd
import matplotlib.pyplot as plt
import mlflow
import hashlib, subprocess
import time

from env.simple_lob_env import SimpleLOBEnv
from agents.inventory_mm import InventoryAwareMarketMaker
from utils.seeding import set_global_seed
from utils.io import create_run_dir, save_config, save_dataframe, save_metrics
from utils.metrics import sharpe, max_drawdown, hit_rate
from storage.duckdb import save_metrics as db_save_metrics, save_trades as db_save_trades, init_db as db_init, upsert_run as db_upsert_run
from risk.manager import RiskManager, RiskConfig
from config.schema import load_config


def run_backtest(cfg: dict) -> tuple[Path, dict]:
    # Ensure DuckDB tables exist
    db_init()

    # Seed and run dir
    set_global_seed(cfg.get('seed'))
    run_dir = create_run_dir(cfg.get('output_dir', 'results'), cfg.get('run_tag', ''))
    config_path = save_config(cfg, run_dir)

    # Environment and agent
    env = SimpleLOBEnv(
        seed=cfg.get('seed'),
        market=cfg.get('market'),
        execution=cfg.get('execution'),
        fees=cfg.get('fees'),
    )
    agent_cfg = cfg.get('agent', {})
    agent = InventoryAwareMarketMaker(
        spread=agent_cfg.get('spread', 0.1),
        inventory_sensitivity=agent_cfg.get('inventory_sensitivity', 0.05)
    )

    risk_cfg = cfg.get('risk') or {}
    risk = RiskManager(RiskConfig(max_inventory=risk_cfg.get('max_inventory', 50), max_drawdown=risk_cfg.get('max_drawdown', 0.2)))

    steps = int(cfg.get('steps', 1000))
    for _ in range(steps):
        if not risk.check(env.inventory, env.pnl):
            break
        bid, ask = agent.quote(env.mid_price, env.inventory)
        env.step(bid, ask)

    df = pd.DataFrame(env.history)
    csv_path = save_dataframe(df, run_dir, 'inventory_mm_run.csv')

    # Metrics
    returns = df['pnl'].diff().fillna(0.0).values
    metrics = {
        'final_pnl': float(df['pnl'].iloc[-1]),
        'final_inventory': int(df['inventory'].iloc[-1]),
        'std_inventory': float(df['inventory'].std()),
        'sharpe': sharpe(returns),
        'max_drawdown': max_drawdown(df['pnl'].values),
        'hit_rate': hit_rate(returns),
        'steps': steps
    }
    metrics_path = save_metrics(metrics, run_dir)

    # Plot
    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.plot(df['time'], df['pnl'])
    plt.title("PnL over time")

    plt.subplot(2, 1, 2)
    plt.plot(df['time'], df['inventory'])
    plt.title('Inventory over time')
    plt.tight_layout()
    plot_path = run_dir / "inventory_mm_plot.png"
    plt.savefig(plot_path)

    # MLflow logging
    mlflow.set_experiment(cfg.get('run_tag', 'mmrl'))
    run_id = None
    with mlflow.start_run(run_name='backtest') as active_run:
        # Params
        mlflow.log_params({
            'seed': cfg.get('seed'),
            'steps': steps,
            'agent_spread': agent_cfg.get('spread', 0.1),
            'agent_inventory_sensitivity': agent_cfg.get('inventory_sensitivity', 0.05),
            'tick_size': getattr(env, 'tick_size', None),
            'max_inventory': getattr(env, 'max_inventory', None),
        })
        # Nested dicts as strings for quick logging
        mlflow.log_param('market', str(cfg.get('market')))
        mlflow.log_param('execution', str(cfg.get('execution')))
        mlflow.log_param('fees', str(cfg.get('fees')))

        # Metrics
        mlflow.log_metrics(metrics)

        # Artifacts
        mlflow.log_artifact(str(config_path))
        mlflow.log_artifact(str(csv_path))
        mlflow.log_artifact(str(plot_path))
        mlflow.log_artifacts(str(run_dir))
        run_id = active_run.info.run_id

    # Write run_id to file and persist to DuckDB
    if run_id:
        (run_dir / 'mlflow_run_id.txt').write_text(run_id)
    db_save_metrics(run_dir.name, cfg.get('run_tag', 'mmrl'), metrics)
    db_save_trades(run_dir.name, df)

    # Repro stamps
    try:
        commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
    except Exception:
        commit_hash = None
    config_bytes = open(cfg_path, 'rb').read()
    config_hash = hashlib.sha256(config_bytes).hexdigest()
    freeze_txt = subprocess.check_output([sys.executable, "-m", "pip", "freeze"]).decode()
    (run_dir / 'commit.txt').write_text(commit_hash or '')
    (run_dir / 'config_hash.txt').write_text(config_hash)
    (run_dir / 'pip_freeze.txt').write_text(freeze_txt)
    # Persist run metadata to DB
    db_upsert_run({
        "id": run_dir.name,
        "type": "backtest",
        "experiment": cfg.get('run_tag', 'mmrl'),
        "run_dir": str(run_dir),
        "mlflow_run_id": run_id,
        "status": "completed",
        "payload": cfg,
        "metrics": metrics,
        "submitted_at": None,
        "started_at": None,
        "finished_at": time.time(),
        "metadata": {"pip_freeze": True},
        "commit_hash": commit_hash,
        "config_hash": config_hash,
    })

    print(f"Saved artifacts to: {run_dir}")
    print(metrics)
    return run_dir, metrics


def main():
    # Load config (allow override via env)
    cfg_path = os.environ.get('MMRL_CONFIG', 'configs/inventory.yaml')
    cfg = load_config(cfg_path).model_dump()
    run_backtest(cfg)


if __name__ == "__main__":
    main()
