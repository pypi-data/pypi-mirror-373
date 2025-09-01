import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import yaml
import optuna
import mlflow
import numpy as np
import pandas as pd
from utils.io import create_run_dir, save_config, save_dataframe
from utils.metrics import sharpe, max_drawdown, hit_rate
from env.simple_lob_env import SimpleLOBEnv
from agents.inventory_mm import InventoryAwareMarketMaker


def run_sim(cfg: dict, spread: float, inv_sense: float, steps: int) -> dict:
    env = SimpleLOBEnv(seed=cfg.get('seed'), market=cfg.get('market'), execution=cfg.get('execution'), fees=cfg.get('fees'))
    agent = InventoryAwareMarketMaker(spread=spread, inventory_sensitivity=inv_sense)
    for _ in range(steps):
        bid, ask = agent.quote(env.mid_price, env.inventory)
        env.step(bid, ask)
    df = pd.DataFrame(env.history)
    returns = df['pnl'].diff().fillna(0.0).values
    return {
        'final_pnl': float(df['pnl'].iloc[-1]),
        'sharpe': sharpe(returns),
        'max_drawdown': max_drawdown(df['pnl'].values),
        'hit_rate': hit_rate(returns),
        'std_inventory': float(df['inventory'].std()),
    }


def objective(trial: optuna.Trial, cfg: dict) -> float:
    spread = trial.suggest_float('spread', 0.01, 0.2)
    inv_sense = trial.suggest_float('inventory_sensitivity', 0.001, 0.08)
    steps = int(cfg.get('steps', 1000))
    res = run_sim(cfg, spread, inv_sense, steps)
    # Constrain drawdown and inventory
    if res['max_drawdown'] > cfg.get('risk', {}).get('max_drawdown', 0.2):
        return -1e9
    if res['std_inventory'] > cfg.get('risk', {}).get('max_inv_std', 20.0):
        return -1e9
    # Maximize Sharpe subject to penalties
    score = res['sharpe'] - 0.001 * res['std_inventory'] + 0.0001 * res['final_pnl']
    trial.set_user_attr('metrics', res)
    return score


def main():
    cfg_path = os.environ.get('MMRL_CONFIG', 'configs/inventory.yaml')
    with open(cfg_path, 'r') as f:
        cfg = yaml.safe_load(f)

    mlflow.set_experiment(cfg.get('run_tag', 'mmrl'))
    study = optuna.create_study(direction='maximize')
    with mlflow.start_run(run_name='hyperopt_rule_based'):
        study.optimize(lambda t: objective(t, cfg), n_trials=30)
        best = study.best_trial
        best_params = best.params
        best_metrics = best.user_attrs.get('metrics', {})
        mlflow.log_params(best_params)
        mlflow.log_metrics(best_metrics)
        print('Best params:', best_params)
        print('Metrics:', best_metrics)


if __name__ == '__main__':
    main()