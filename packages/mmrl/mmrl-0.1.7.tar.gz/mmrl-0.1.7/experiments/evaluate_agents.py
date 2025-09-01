import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import yaml
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mlflow
from env.simple_lob_env import SimpleLOBEnv
from agents.inventory_mm import InventoryAwareMarketMaker
from utils.metrics import sharpe, max_drawdown, hit_rate
from stable_baselines3 import PPO
from env.gym_env import MarketMakingGymEnv
from agents.naive_mm import NaiveMarketMaker
from agents.avellaneda_stoikov import AvellanedaStoikovMM
from agents.mean_reversion_mm import MeanReversionMarketMaker
from agents.momentum_mm import MomentumMarketMaker


def evaluate_rule_based(cfg: dict, steps: int) -> dict:
    env = SimpleLOBEnv(seed=cfg.get('seed'), market=cfg.get('market'), execution=cfg.get('execution'), fees=cfg.get('fees'))
    agent_cfg = cfg.get('agent', {})
    agent = InventoryAwareMarketMaker(spread=agent_cfg.get('spread', 0.1), inventory_sensitivity=agent_cfg.get('inventory_sensitivity', 0.05))
    for _ in range(steps):
        bid, ask = agent.quote(env.mid_price, env.inventory)
        env.step(bid, ask)
    df = pd.DataFrame(env.history)
    returns = df['pnl'].diff().fillna(0.0).values
    return {
        'final_pnl': float(df['pnl'].iloc[-1]),
        'std_inventory': float(df['inventory'].std()),
        'sharpe': sharpe(returns),
        'max_drawdown': max_drawdown(df['pnl'].values),
        'hit_rate': hit_rate(returns),
    }


def evaluate_ppo(cfg: dict, steps: int, model_path: str) -> dict:
    env = MarketMakingGymEnv(cfg)
    model = PPO.load(model_path)
    obs, _ = env.reset()
    for _ in range(steps):
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        if terminated or truncated:
            break
    # Extract metrics from underlying env
    hist = getattr(env.env, 'history', [])
    if not hist:
        return {'final_pnl': 0.0, 'std_inventory': 0.0, 'sharpe': 0.0, 'max_drawdown': 0.0, 'hit_rate': 0.0}
    df = pd.DataFrame(hist)
    returns = df['pnl'].diff().fillna(0.0).values
    return {
        'final_pnl': float(df['pnl'].iloc[-1]),
        'std_inventory': float(df['inventory'].std()),
        'sharpe': sharpe(returns),
        'max_drawdown': max_drawdown(df['pnl'].values),
        'hit_rate': hit_rate(returns),
    }


def evaluate_naive(cfg: dict, steps: int) -> dict:
    env = SimpleLOBEnv(seed=cfg.get('seed'), market=cfg.get('market'), execution=cfg.get('execution'), fees=cfg.get('fees'))
    agent = NaiveMarketMaker(spread=cfg.get('agent', {}).get('spread', 0.1))
    for _ in range(steps):
        bid, ask = agent.quote(env.mid_price, env.inventory)
        env.step(bid, ask)
    df = pd.DataFrame(env.history)
    returns = df['pnl'].diff().fillna(0.0).values
    return {
        'final_pnl': float(df['pnl'].iloc[-1]),
        'std_inventory': float(df['inventory'].std()),
        'sharpe': sharpe(returns),
        'max_drawdown': max_drawdown(df['pnl'].values),
        'hit_rate': hit_rate(returns),
    }


def evaluate_mean_reversion(cfg: dict, steps: int) -> dict:
    env = SimpleLOBEnv(seed=cfg.get('seed'), market=cfg.get('market'), execution=cfg.get('execution'), fees=cfg.get('fees'))
    agent = MeanReversionMarketMaker(target_spread=cfg.get('agent', {}).get('spread', 0.1), kappa=0.1, skew_sensitivity=0.05)
    for _ in range(steps):
        bid, ask = agent.quote(env.mid_price, env.inventory)
        env.step(bid, ask)
    df = pd.DataFrame(env.history)
    returns = df['pnl'].diff().fillna(0.0).values
    return {
        'final_pnl': float(df['pnl'].iloc[-1]),
        'std_inventory': float(df['inventory'].std()),
        'sharpe': sharpe(returns),
        'max_drawdown': max_drawdown(df['pnl'].values),
        'hit_rate': hit_rate(returns),
    }


def evaluate_momentum(cfg: dict, steps: int) -> dict:
    env = SimpleLOBEnv(seed=cfg.get('seed'), market=cfg.get('market'), execution=cfg.get('execution'), fees=cfg.get('fees'))
    agent = MomentumMarketMaker(spread=cfg.get('agent', {}).get('spread', 0.12), window=20, bias=0.05)
    for _ in range(steps):
        bid, ask = agent.quote(env.mid_price, env.inventory)
        env.step(bid, ask)
    df = pd.DataFrame(env.history)
    returns = df['pnl'].diff().fillna(0.0).values
    return {
        'final_pnl': float(df['pnl'].iloc[-1]),
        'std_inventory': float(df['inventory'].std()),
        'sharpe': sharpe(returns),
        'max_drawdown': max_drawdown(df['pnl'].values),
        'hit_rate': hit_rate(returns),
    }


def evaluate_avellaneda(cfg: dict, steps: int) -> dict:
    env = SimpleLOBEnv(seed=cfg.get('seed'), market=cfg.get('market'), execution=cfg.get('execution'), fees=cfg.get('fees'))
    as_cfg = cfg.get('avellaneda', { 'risk_aversion': 0.1, 'base_spread': 0.1, 'inv_penalty': 0.05 })
    agent = AvellanedaStoikovMM(**as_cfg)
    for _ in range(steps):
        bid, ask = agent.quote(env.mid_price, env.inventory, sigma=getattr(env, '_current_sigma', 0.5))
        env.step(bid, ask)
    df = pd.DataFrame(env.history)
    returns = df['pnl'].diff().fillna(0.0).values
    return {
        'final_pnl': float(df['pnl'].iloc[-1]),
        'std_inventory': float(df['inventory'].std()),
        'sharpe': sharpe(returns),
        'max_drawdown': max_drawdown(df['pnl'].values),
        'hit_rate': hit_rate(returns),
    }


def main():
    cfg_path = os.environ.get('MMRL_CONFIG', 'configs/inventory.yaml')
    with open(cfg_path, 'r') as f:
        cfg = yaml.safe_load(f)
    steps = int(cfg.get('steps', 1000))

    mlflow.set_experiment(cfg.get('run_tag', 'mmrl'))
    with mlflow.start_run(run_name='evaluate_agents'):
        naive = evaluate_naive(cfg, steps)
        rb = evaluate_rule_based(cfg, steps)
        asmm = evaluate_avellaneda(cfg, steps)
        mr = evaluate_mean_reversion(cfg, steps)
        mom = evaluate_momentum(cfg, steps)
        ppo_path = os.path.join(cfg.get('output_dir', 'results'), 'ppo_market_making.zip')
        if os.path.exists(ppo_path):
            ppo = evaluate_ppo(cfg, steps, ppo_path)
        else:
            ppo = {'final_pnl': None, 'std_inventory': None, 'sharpe': None, 'max_drawdown': None, 'hit_rate': None}

        # Log metrics
        mlflow.log_metrics({f"naive_{k}": v for k, v in naive.items() if v is not None})
        mlflow.log_metrics({f"rb_{k}": v for k, v in rb.items() if v is not None})
        mlflow.log_metrics({f"as_{k}": v for k, v in asmm.items() if v is not None})
        mlflow.log_metrics({f"mr_{k}": v for k, v in mr.items() if v is not None})
        mlflow.log_metrics({f"mom_{k}": v for k, v in mom.items() if v is not None})
        mlflow.log_metrics({f"ppo_{k}": v for k, v in ppo.items() if v is not None})

        # Plot comparison
        labels = ['final_pnl', 'sharpe', 'max_drawdown']
        x = np.arange(len(labels))
        width = 0.14
        plt.figure(figsize=(12, 4))
        series = [
            ('Naive', naive),
            ('Rule-Based', rb),
            ('A-S', asmm),
            ('MeanRev', mr),
            ('Momentum', mom),
            ('PPO', ppo),
        ]
        for i, (name, vals) in enumerate(series):
            v = [vals.get(k, 0) or 0 for k in labels]
            plt.bar(x + (i - (len(series)-1)/2)*width, v, width, label=name)
        plt.xticks(x, labels)
        plt.legend()
        plt.tight_layout()
        out_dir = cfg.get('output_dir', 'results')
        os.makedirs(out_dir, exist_ok=True)
        plot_path = os.path.join(out_dir, 'evaluate_comparison.png')
        plt.savefig(plot_path)
        mlflow.log_artifact(plot_path)

        print('Naive:', naive)
        print('Rule-based:', rb)
        print('Avellaneda-Stoikov:', asmm)
        print('MeanReversion:', mr)
        print('Momentum:', mom)
        print('PPO:', ppo)


if __name__ == '__main__':
    main()