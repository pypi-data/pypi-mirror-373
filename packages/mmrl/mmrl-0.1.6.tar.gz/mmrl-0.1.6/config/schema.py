from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import yaml


class OUModel(BaseModel):
    mu: float = 100.0
    kappa: float = 0.05
    sigma: float = 0.5
    dt: float = 1.0


class VolRegime(BaseModel):
    enabled: bool = True
    high_sigma_scale: float = 3.0
    switch_prob: float = 0.02


class MarketConfig(BaseModel):
    ou_enabled: bool = True
    ou: OUModel = OUModel()
    vol_regime: VolRegime = VolRegime()
    correlation: Optional[List[List[float]]] = None


class ExecutionConfig(BaseModel):
    base_arrival_rate: float = 1.0
    alpha: float = 1.5
    alpha_grid: Optional[List[float]] = None
    size_sensitivity: float = 0.1


class FeesConfig(BaseModel):
    fee_bps: float = 1.0
    slippage_bps: float = 2.0
    maker_bps: float = -0.5
    taker_bps: float = 1.0


class AgentConfig(BaseModel):
    spread: float = 0.1
    inventory_sensitivity: float = 0.05


class MultiAssetConfig(BaseModel):
    num_assets: int = 2
    depth_levels: int = 3
    level_widen: float = 0.05
    base_size: float = 1.0
    regime_skew: float = 0.05


class RiskConfig(BaseModel):
    max_inventory: int = 50
    max_drawdown: float = 0.2


class AppConfig(BaseModel):
    run_tag: str = "mmrl"
    seed: int = 42
    steps: int = 1000
    output_dir: str = "results"
    market: MarketConfig = MarketConfig()
    execution: ExecutionConfig = ExecutionConfig()
    fees: FeesConfig = FeesConfig()
    agent: AgentConfig = AgentConfig()
    grid: Optional[Dict[str, List[float]]] = None
    multi_asset: Optional[MultiAssetConfig] = None
    risk: Optional[RiskConfig] = None


def load_config(path: str) -> AppConfig:
    with open(path, 'r') as f:
        data = yaml.safe_load(f)
    return AppConfig.model_validate(data)


def export_json_schema() -> Dict[str, Any]:
    return AppConfig.model_json_schema()