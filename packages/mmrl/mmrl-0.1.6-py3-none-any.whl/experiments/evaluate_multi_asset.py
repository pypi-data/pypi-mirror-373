import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import yaml
import numpy as np
import pandas as pd
import mlflow
from utils.io import create_run_dir, save_config, save_dataframe
from env.multi_asset_env import MultiAssetEnv
from agents.depth_mm import DepthAwareMarketMaker
from utils.metrics import sharpe, max_drawdown, hit_rate


def main():
    cfg_path = os.environ.get('MMRL_CONFIG', 'configs/inventory.yaml')
    with open(cfg_path, 'r') as f:
        cfg = yaml.safe_load(f)

    num_assets = cfg.get('multi_asset', {}).get('num_assets', 2)
    depth_levels = cfg.get('multi_asset', {}).get('depth_levels', 3)

    env = MultiAssetEnv(
        num_assets=num_assets,
        depth_levels=depth_levels,
        seed=cfg.get('seed'),
        market=cfg.get('market'),
        execution=cfg.get('execution'),
        fees=cfg.get('fees'),
    )
    agent = DepthAwareMarketMaker(
        depth_levels=depth_levels,
        base_spread=cfg.get('agent', {}).get('spread', 0.1),
        level_widen=cfg.get('multi_asset', {}).get('level_widen', 0.05),
        base_size=cfg.get('multi_asset', {}).get('base_size', 1.0),
        inv_sensitivity=cfg.get('agent', {}).get('inventory_sensitivity', 0.02),
        regime_skew=cfg.get('multi_asset', {}).get('regime_skew', 0.05),
    )

    steps = int(cfg.get('steps', 1000))
    for _ in range(steps):
        bids, asks = agent.quote(env.mid, env.inventory, env._sigma_scale)
        env.step(bids, asks)

    # Convert history to DataFrame with stringified arrays for CSV
    hist = []
    for rec in env.history:
        hist.append({
            'time': rec['time'],
            'mid': rec['mid'].tolist(),
            'inventory': rec['inventory'].tolist(),
            'pnl': rec['pnl'],
            'sigma_scale': rec['sigma_scale'].tolist(),
        })
    df = pd.DataFrame(hist)

    returns = df['pnl'].diff().fillna(0.0).values
    summary = {
        'final_pnl': float(df['pnl'].iloc[-1]),
        'std_inventory': float(np.std(np.linalg.norm(np.stack(df['inventory'].values), axis=1))),
        'sharpe': sharpe(returns),
        'max_drawdown': max_drawdown(df['pnl'].values),
        'hit_rate': hit_rate(returns),
    }

    # Save to run dir and log to MLflow
    run_dir = create_run_dir(cfg.get('output_dir', 'results'), f"{cfg.get('run_tag','')}_multi")
    save_config(cfg, run_dir)
    csv_path = save_dataframe(df, run_dir, 'multi_asset_history.csv')

    mlflow.set_experiment(cfg.get('run_tag', 'mmrl'))
    with mlflow.start_run(run_name='evaluate_multi_asset'):
        mlflow.log_metrics(summary)
        mlflow.log_artifact(str(csv_path))
        mlflow.log_artifacts(str(run_dir))

    print('Multi-asset summary:', summary)


if __name__ == '__main__':
    main()