from pathlib import Path
from datetime import datetime
import json
import yaml
import pandas as pd

def create_run_dir(base_dir: str = 'results', tag: str = '') -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_tag = f'_{tag}' if tag else ''
    run_dir = Path(base_dir) / f'{ts}{safe_tag}'
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir

def save_config(cfg: dict, run_dir: Path, name: str = 'config.yaml') -> Path:
    path = run_dir / name
    with open(path, "w") as f:
        yaml.safe_dump(cfg, f, sort_keys=False)
    return path

def save_metrics(metrics: dict, run_dir: Path, name: str = 'metrics.json') -> Path:
    path = run_dir / name
    with open(path, 'w') as f:
        json.dump(metrics, f, indent=2)
    return path

def save_dataframe(df: pd.DataFrame, run_dir: Path, name: str) -> Path:
    path = run_dir / name
    df.to_csv(path, index=False)
    return path
