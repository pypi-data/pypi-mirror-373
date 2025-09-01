# Market Making RL Agent

![PyPI](https://img.shields.io/pypi/v/mmrl.svg)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Docs: https://Aviral1303.github.io/Market-Making-RL-Agent/

## Why this is useful
- End-to-end, deployable research stack: config-driven envs, MLflow tracking, CLI, REST API with async jobs, and DuckDB persistence
- Microstructure features that matter: OU price dynamics with regime switching, probabilistic fills, fees/slippage, multi-asset correlation, depth-aware quoting, size decisions
- Baselines and RL: Naive, Inventory-aware, Avellaneda–Stoikov, PPO; hyperparameter search with Optuna

## At a glance
![Demo](https://raw.githubusercontent.com/Aviral1303/Market-Making-RL-Agent/main/docs/assets/demo.gif)

### Benchmarks (best-of grid)
![Benchmarks](https://raw.githubusercontent.com/Aviral1303/Market-Making-RL-Agent/main/docs/assets/benchmarks.png)

## 60s Quickstart
```
pip install mmrl
mmrl backtest
mmrl evaluate  # Naive vs Rule-Based vs A–S vs PPO
mmrl analyze strategy_comparison.csv --plot  # analyze your returns file
```
## Examples
- Backtest + HTML report in one go
```
mmrl backtest
mmrl report results/$(ls -t results | head -n 1) --out report.html
```

- Run grid search and visualize
```
mmrl grid
python3 analysis/plot_grid_heatmaps.py
```

- Compare agents (rule-based and PPO if rl extra installed)
```
mmrl evaluate
```

- Programmatic backtest
```python
from mmrl import run_backtest
cfg = {"run_tag": "script", "seed": 7, "steps": 1000, "output_dir": "results",
        "agent": {"spread": 0.1, "inventory_sensitivity": 0.05},
        "market": {"ou_enabled": True, "ou": {"mu": 100, "kappa": 0.05, "sigma": 0.5, "dt": 1.0},
                    "vol_regime": {"enabled": True, "high_sigma_scale": 3.0, "switch_prob": 0.02}},
        "execution": {"base_arrival_rate": 1.0, "alpha": 1.5},
        "fees": {"fee_bps": 1.0, "slippage_bps": 2.0, "maker_bps": -0.5, "taker_bps": 1.0}}
run_dir, metrics = run_backtest(cfg)
print(run_dir, metrics)
```

- Plug in your own data (CSV example)
```python
from env.simple_lob_env import SimpleLOBEnv
from mmrl.data import load_adapter

env = SimpleLOBEnv()
adapter = load_adapter('mmrl.data.csv_adapter:CSVAdapter', path='data/example.csv', mapping={'mid_price': 'mid', 'best_bid': 'bid', 'best_ask': 'ask'})
for tick in adapter.iter_ticks():
    state = env.step_from_tick(tick)
```
## Programmatic API (Python)
```python
from mmrl import run_backtest

cfg = {
  "run_tag": "demo", "seed": 42, "steps": 500, "output_dir": "results",
  "agent": {"spread": 0.1, "inventory_sensitivity": 0.05},
  "market": {"ou_enabled": True, "ou": {"mu": 100, "kappa": 0.05, "sigma": 0.5, "dt": 1.0},
              "vol_regime": {"enabled": True, "high_sigma_scale": 3.0, "switch_prob": 0.02}},
  "execution": {"base_arrival_rate": 1.0, "alpha": 1.5},
  "fees": {"fee_bps": 1.0, "slippage_bps": 2.0, "maker_bps": -0.5, "taker_bps": 1.0}
}
run_dir, metrics = run_backtest(cfg)
print(run_dir, metrics)
```

From source:
```
pip install -r requirements.txt
```

## Colab Notebooks
- Quickstart
  
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Aviral1303/Market-Making-RL-Agent/blob/main/notebooks/Quickstart.ipynb)

- Grid Search + Heatmaps
  
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Aviral1303/Market-Making-RL-Agent/blob/main/notebooks/Grid_Heatmaps.ipynb)

- RL vs Rule-Based
  
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Aviral1303/Market-Making-RL-Agent/blob/main/notebooks/RL_vs_RuleBased.ipynb)

- Multi-asset & Replay
  
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Aviral1303/Market-Making-RL-Agent/blob/main/notebooks/MultiAsset_Replay.ipynb)

## Multi-asset
- Configure under `multi_asset` in `configs/inventory.yaml`
- Run:
```
python3 experiments/evaluate_multi_asset.py
python3 analysis/plot_multi_asset.py results/.../multi_asset_history.csv
```

## API
- Start stack:
```
docker compose up -d redis worker api mlflow
curl http://localhost:8000/health
curl http://localhost:8000/config/schema  # config JSON schema
```
- Submit jobs:
```
curl -X POST http://localhost:8000/backtest -H 'Content-Type: application/json' -d '{"steps": 200}'
curl -X POST http://localhost:8000/grid -H 'Content-Type: application/json' -d '{"execution": {"alpha_grid": [1.0, 1.5]}}'
curl http://localhost:8000/trades/<run_id>?limit=100
curl http://localhost:8000/runs/<run_dir_name>/artifacts
curl -L -o run.zip http://localhost:8000/runs/<run_dir_name>/download
```

## Hyperparameter Optimization
```
python3 experiments/hyperopt.py
```

## Notable features
- Multi-asset Gym wrapper with per-asset, per-level actions (offsets + sizes)
- Depth-aware agent placing quotes at multiple levels with regime-conditioned parameters
- DuckDB persistence of runs/metrics/trades and a `/trades/{run_id}` endpoint
- MLflow logging of params, metrics, artifacts with run IDs written per run
- CLI extras: `mmrl fetch-data` (CCXT sample), `mmrl config-validate`, `mmrl config-schema`

## Roadmap
- Postgres-backed storage and public demo deployment
- Size-aware RL policy across multi-asset Gym env
- Notebooks + Colab badges for quick experimentation

## Packaging
- Install from source or build wheel with `python -m build` (requires `build`).
- Optional extras:
  - `mmrl[api]` for FastAPI stack
  - `mmrl[rl]` for Gymnasium/SB3

## Data utilities
- Fetch sample trades to Parquet:
```
python3 -m mmrl.cli fetch-data --exchange binance --symbol BTC/USDT --limit 1000 --out data/btcusdt.parquet
```
