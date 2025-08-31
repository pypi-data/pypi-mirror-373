from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, Optional
import subprocess
import tempfile
import os
import yaml


def load_base_config() -> Dict[str, Any]:
    with open("configs/inventory.yaml", "r") as f:
        return yaml.safe_load(f)


def merge_overrides(base: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(base)
    for k, v in (overrides or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = merge_overrides(out[k], v)
        else:
            out[k] = v
    return out


def run_with_config(cli_args: list[str], cfg: Optional[Dict[str, Any]] = None):
    env = os.environ.copy()
    tmpfile = None
    if cfg is not None:
        fd, path = tempfile.mkstemp(prefix="mmrl_cfg_", suffix=".yaml")
        with os.fdopen(fd, "w") as f:
            yaml.safe_dump(cfg, f, sort_keys=False)
        env["MMRL_CONFIG"] = path
        tmpfile = path
    try:
        subprocess.run(cli_args, check=True, env=env)
    finally:
        if tmpfile and Path(tmpfile).exists():
            try:
                Path(tmpfile).unlink()
            except Exception:
                pass