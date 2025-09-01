import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import yaml
from tqdm import tqdm
import numpy as np
import pandas as pd
import mlflow

from env.simple_lob_env import SimpleLOBEnv
from agents.inventory_mm import InventoryAwareMarketMaker
from utils.seeding import set_global_seed
from utils.io import create_run_dir, save_config, save_dataframe
from utils.metrics import sharpe, max_drawdown, hit_rate
from storage.duckdb import save_metrics as db_save_metrics
from config.schema import load_config


def run_simulation(spread, sensitivity, steps=1000, seed=None, market=None, execution=None, fees=None):
    env = SimpleLOBEnv(seed=seed, market=market, execution=execution, fees=fees)
    agent = InventoryAwareMarketMaker(spread=spread, inventory_sensitivity=sensitivity)

    for _ in range(steps):
        bid, ask = agent.quote(env.mid_price, env.inventory)
        env.step(bid, ask)

    df = pd.DataFrame(env.history)
    returns = df['pnl'].diff().fillna(0.0).values
    trades = df[['executed_bid', 'executed_ask']].notna().sum(axis=1).sum()
    fill_rate = float(trades) / float(steps)
    return {
        'spread': spread,
        'sensitivity': sensitivity,
        'alpha': execution.get('alpha') if execution else None,
        'final_pnl': float(df['pnl'].iloc[-1]),
        'final_inventory': int(df['inventory'].iloc[-1]),
        'std_inventory': float(df['inventory'].std()),
        'sharpe': sharpe(returns),
        'max_drawdown': max_drawdown(df['pnl'].values),
        'hit_rate': hit_rate(returns),
        'trades': int(trades),
        'fill_rate': fill_rate,
    }


def main():
    cfg_path = 'configs/inventory.yaml'
    cfg = load_config(cfg_path).model_dump()

    seed = cfg.get('seed', 42)
    set_global_seed(seed)

    run_dir = create_run_dir(cfg.get('output_dir', 'results'), f"{cfg.get('run_tag','')}_grid")
    config_path = save_config(cfg, run_dir)

    spreads = cfg['grid']['spread']
    sensitivities = cfg['grid']['sensitivity']
    steps = int(cfg.get('steps', 1000))

    exec_base = cfg.get('execution', {})
    alpha_grid = exec_base.get('alpha_grid', [exec_base.get('alpha', 1.5)])

    mlflow.set_experiment(cfg.get('run_tag', 'mmrl'))
    with mlflow.start_run(run_name='grid_sweep'):
        mlflow.log_param('seed', seed)
        mlflow.log_param('steps', steps)
        mlflow.log_param('market', str(cfg.get('market')))
        mlflow.log_param('fees', str(cfg.get('fees')))
        mlflow.log_param('alpha_grid', str(alpha_grid))
        mlflow.log_param('spreads', str(spreads))
        mlflow.log_param('sensitivities', str(sensitivities))

        results = []
        for alpha in tqdm(alpha_grid, desc='alpha'):
            for s in spreads:
                for inv_s in sensitivities:
                    exec_cfg = dict(exec_base)
                    exec_cfg['alpha'] = float(alpha)
                    results.append(
                        run_simulation(
                            spread=s,
                            sensitivity=inv_s,
                            steps=steps,
                            seed=seed,
                            market=cfg.get('market'),
                            execution=exec_cfg,
                            fees=cfg.get('fees'),
                        )
                    )

        results_df = pd.DataFrame(results)
        csv_path = save_dataframe(results_df, run_dir, 'grid_search_results.csv')
        mlflow.log_artifact(str(config_path))
        mlflow.log_artifact(str(csv_path))
        mlflow.log_artifacts(str(run_dir))
        # Persist aggregate metrics per (spread,sensitivity,alpha) row as key-suffixed metrics using run_dir name as id
        agg = {
            'rows': len(results_df),
            'best_final_pnl': float(results_df['final_pnl'].max()),
            'best_sharpe': float(results_df['sharpe'].max()),
            'avg_fill_rate': float(results_df['fill_rate'].mean()) if 'fill_rate' in results_df.columns else 0.0,
        }
        db_save_metrics(run_dir.name, cfg.get('run_tag', 'mmrl'), agg)

    print(f"Saved grid search results to: {run_dir}")


if __name__ == "__main__":
    main()