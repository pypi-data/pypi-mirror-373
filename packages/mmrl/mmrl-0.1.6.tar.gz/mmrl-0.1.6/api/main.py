from fastapi import FastAPI, HTTPException, Body, Depends, Header
from fastapi.responses import JSONResponse, PlainTextResponse, StreamingResponse
from pathlib import Path
import json
import time
from typing import List, Optional, Dict, Any
import os
from prometheus_client import CollectorRegistry, Counter, generate_latest, Summary, Gauge
from pydantic import BaseModel, Field
# Local utilities for config handling and process exec
from api.utils import merge_overrides, run_with_config
from api.jobs import create_job, update_job, get_job, list_jobs
from api.queue import get_queue
from storage.duckdb import init_db as init_duckdb, upsert_run as db_upsert_run, list_runs as db_list_runs, save_trades as db_save_trades, count_runs as db_count_runs
import duckdb
from config.schema import AppConfig, load_config as load_cfg_model
from config.schema import export_json_schema

app = FastAPI(title="MMRL API", version="0.1.0")

# Init DB
init_duckdb()

# Metrics
registry = CollectorRegistry()
RUNS_TOTAL = Counter("mmrl_runs_total", "Number of backtest runs", registry=registry)
GRIDS_TOTAL = Counter("mmrl_grids_total", "Number of grid runs", registry=registry)

JOB_DURATION = Summary("mmrl_job_duration_seconds", "Duration of async jobs", registry=registry)
JOB_FAILURES = Counter("mmrl_job_failures_total", "Number of job failures", registry=registry)
RUN_ERRORS_TOTAL = Counter("mmrl_run_errors_total", "Number of backtest run errors", registry=registry)
RUN_IN_PROGRESS = Gauge("mmrl_runs_in_progress", "Backtests currently in progress", registry=registry)


class ExecutionOverrides(BaseModel):
    base_arrival_rate: Optional[float] = Field(default=None, ge=0)
    alpha: Optional[float] = Field(default=None, ge=0)
    alpha_grid: Optional[List[float]] = None


class AgentOverrides(BaseModel):
    spread: Optional[float] = Field(default=None, ge=0)
    inventory_sensitivity: Optional[float] = Field(default=None, ge=0)


class Overrides(BaseModel):
    seed: Optional[int] = None
    steps: Optional[int] = Field(default=None, ge=1)
    agent: Optional[AgentOverrides] = None
    execution: Optional[ExecutionOverrides] = None


def bearer_auth(authorization: Optional[str] = Header(default=None)):
    expected = os.environ.get("MMRL_API_TOKEN")
    if not expected:
        return  # auth disabled
    if authorization != f"Bearer {expected}":
        raise HTTPException(status_code=401, detail="unauthorized")


def get_run_dirs(results_root: Path = Path("results")) -> List[Path]:
    if not results_root.exists():
        return []
    run_dirs = [p for p in results_root.iterdir() if p.is_dir()]
    run_dirs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return run_dirs


def get_latest_run_dir(results_root: Path = Path("results")) -> Optional[Path]:
    run_dirs = get_run_dirs(results_root)
    return run_dirs[0] if run_dirs else None


def last_mlflow_run_id() -> Optional[str]:
    # Heuristic: read latest run dir from ./mlruns (local tracking). For real use, query MLflow API.
    root = Path("mlruns")
    if not root.exists():
        return None
    candidates = sorted(root.rglob("meta.yaml"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        return None
    # run_id is parent dir name of meta.yaml
    return candidates[0].parent.name


def last_mlflow_run_id_from_run_dir(run_dir: Path) -> Optional[str]:
    p = run_dir / 'mlflow_run_id.txt'
    if p.exists():
        try:
            return p.read_text().strip()
        except Exception:
            return None
    return None


def mlflow_info(cfg: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "mlflow_experiment": cfg.get("run_tag", "mmrl"),
        "mlflow_run_id": last_mlflow_run_id(),
        "mlflow_ui": os.environ.get("MLFLOW_UI_URL", "http://localhost:5000"),
    }


def load_base_config() -> Dict[str, Any]:
    cfg_path = os.environ.get("MMRL_CONFIG", "configs/inventory.yaml")
    cfg = load_cfg_model(cfg_path)
    return cfg.model_dump()


@app.get("/config/schema")
def get_config_schema():
    try:
        return export_json_schema()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    return PlainTextResponse(generate_latest(registry), media_type="text/plain; version=0.0.4")


@app.get("/runs")
def list_runs_endpoint(limit: int = 20, offset: int = 0, experiment: Optional[str] = None, start_ts: Optional[float] = None, end_ts: Optional[float] = None):
    total = db_count_runs(experiment=experiment, start_ts=start_ts, end_ts=end_ts)
    runs = db_list_runs(experiment=experiment, start_ts=start_ts, end_ts=end_ts, limit=limit, offset=offset)
    return {"total": total, "limit": limit, "offset": offset, "runs": runs}


@app.get("/runs/{run_name}")
def get_run_endpoint(run_name: str):
    run_path = Path("results") / run_name
    if not run_path.exists():
        raise HTTPException(status_code=404, detail="run not found")
    metrics = {}
    mp = run_path / "metrics.json"
    if mp.exists():
        try:
            metrics = json.loads(mp.read_text())
        except Exception:
            metrics = {}
    return {
        "run_dir": str(run_path),
        "metrics": metrics,
        "artifacts": {
            "config": str(run_path / "config.yaml"),
            "csv": str(run_path / "inventory_mm_run.csv"),
            "plot": str(run_path / "inventory_mm_plot.png"),
        },
    }


@app.get("/runs/{run_name}/artifacts")
def list_artifacts(run_name: str):
    run_path = Path("results") / run_name
    if not run_path.exists():
        raise HTTPException(status_code=404, detail="run not found")
    files = []
    for p in run_path.glob("**/*"):
        if p.is_file():
            rel = p.relative_to(run_path)
            files.append(str(rel))
    return {"run_dir": str(run_path), "files": sorted(files)}


@app.get("/runs/{run_name}/download")
def download_artifacts(run_name: str):
    import io, zipfile
    run_path = Path("results") / run_name
    if not run_path.exists():
        raise HTTPException(status_code=404, detail="run not found")
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        for p in run_path.glob("**/*"):
            if p.is_file():
                zf.write(p, arcname=str(p.relative_to(run_path)))
    mem.seek(0)
    headers = {"Content-Disposition": f"attachment; filename={run_name}.zip"}
    return StreamingResponse(mem, media_type="application/zip", headers=headers)


@app.post("/backtest")
def backtest(
    overrides: Optional[Overrides] = Body(default=None),
    auth: None = Depends(bearer_auth),
):
    cfg = load_base_config()
    if overrides is not None:
        cfg = merge_overrides(cfg, json.loads(overrides.model_dump_json(exclude_none=True)))
    try:
        RUN_IN_PROGRESS.inc()
        run_with_config(["mmrl", "backtest"], cfg)
    except Exception as e:
        RUN_ERRORS_TOTAL.inc()
        return JSONResponse(status_code=500, content={"error": f"backtest failed: {e}"})
    finally:
        RUN_IN_PROGRESS.dec()

    RUNS_TOTAL.inc()
    time.sleep(0.1)
    run_dir = get_latest_run_dir()
    if run_dir is None:
        return JSONResponse(status_code=500, content={"error": "no run directory found"})

    metrics_path = run_dir / "metrics.json"
    metrics = {}
    if metrics_path.exists():
        try:
            metrics = json.loads(metrics_path.read_text())
        except Exception:
            metrics = {}

    run_mlflow_id = last_mlflow_run_id_from_run_dir(run_dir) or mlflow_info(cfg).get('mlflow_run_id')
    info = mlflow_info(cfg)
    info['mlflow_run_id'] = run_mlflow_id
    resp = {
        "run_dir": str(run_dir),
        "metrics": metrics,
        "artifacts": {
            "config": str(run_dir / "config.yaml"),
            "csv": str(run_dir / "inventory_mm_run.csv"),
            "plot": str(run_dir / "inventory_mm_plot.png"),
        },
    }
    resp.update(info)
    # persist
    db_upsert_run({
        "id": str(run_dir.name),
        "type": "backtest",
        "experiment": cfg.get("run_tag", "mmrl"),
        "run_dir": str(run_dir),
        "mlflow_run_id": run_mlflow_id,
        "status": "completed",
        "payload": json.loads(overrides.model_dump_json(exclude_none=True)) if overrides else {},
        "metrics": metrics,
        "submitted_at": time.time(),
        "started_at": None,
        "finished_at": time.time(),
    })
    return resp


@app.post("/grid")
def grid(
    overrides: Optional[Overrides] = Body(default=None),
    auth: None = Depends(bearer_auth),
):
    cfg = None
    if overrides is not None:
        base = load_base_config()
        cfg = merge_overrides(base, json.loads(overrides.model_dump_json(exclude_none=True)))

    job_id = create_job("grid", payload=json.loads(overrides.model_dump_json(exclude_none=True)) if overrides else {})
    q = get_queue()
    q.enqueue(_run_grid_job, job_id, cfg, job_timeout=3600)
    GRIDS_TOTAL.inc()
    return {"job_id": job_id, "status": "submitted"}


@app.post("/train")
def train(
    overrides: Optional[Overrides] = Body(default=None),
    auth: None = Depends(bearer_auth),
):
    cfg = None
    if overrides is not None:
        base = load_base_config()
        cfg = merge_overrides(base, json.loads(overrides.model_dump_json(exclude_none=True)))

    job_id = create_job("train", payload=json.loads(overrides.model_dump_json(exclude_none=True)) if overrides else {})
    q = get_queue()
    q.enqueue(_run_train_job, job_id, cfg, job_timeout=7200)
    return {"job_id": job_id, "status": "submitted"}


@app.post("/evaluate")
def evaluate(
    overrides: Optional[Overrides] = Body(default=None),
    auth: None = Depends(bearer_auth),
):
    cfg = None
    if overrides is not None:
        base = load_base_config()
        cfg = merge_overrides(base, json.loads(overrides.model_dump_json(exclude_none=True)))
    job_id = create_job("evaluate", payload=json.loads(overrides.model_dump_json(exclude_none=True)) if overrides else {})
    q = get_queue()
    q.enqueue(_run_evaluate_job, job_id, cfg, job_timeout=1800)
    return {"job_id": job_id, "status": "submitted"}


@app.post("/evaluate_multi")
def evaluate_multi(
    overrides: Optional[Overrides] = Body(default=None),
    auth: None = Depends(bearer_auth),
    sync: bool = False,
):
    cfg = None
    if overrides is not None:
        base = load_base_config()
        cfg = merge_overrides(base, json.loads(overrides.model_dump_json(exclude_none=True)))
    if sync:
        # Synchronous evaluation returning run_dir and CSV path
        try:
            run_with_config(["python3", "experiments/evaluate_multi_asset.py"], cfg)
            time.sleep(0.1)
            run_dir = get_latest_run_dir()
            if run_dir is None:
                return JSONResponse(status_code=500, content={"error": "no run directory found"})
            csv_path = str(run_dir / "multi_asset_history.csv")
            return {"run_dir": str(run_dir), "csv": csv_path}
        except Exception as e:
            return JSONResponse(status_code=500, content={"error": f"evaluate_multi failed: {e}"})
    # Async default
    job_id = create_job("evaluate_multi", payload=json.loads(overrides.model_dump_json(exclude_none=True)) if overrides else {})
    q = get_queue()
    q.enqueue(_run_evaluate_multi_job, job_id, cfg, job_timeout=1800)
    return {"job_id": job_id, "status": "submitted"}


@app.get("/jobs")
def list_jobs_endpoint(limit: int = 50):
    return {"jobs": list_jobs(limit)}


@app.get("/jobs/{job_id}")
def get_job_endpoint(job_id: str):
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return job


@app.get("/trades/{run_id}")
def get_trades(run_id: str, limit: int = 500):
    try:
        con = duckdb.connect(os.environ.get("MMRL_DUCKDB_PATH", "data/mmrl.duckdb"))
        cur = con.execute("SELECT * FROM trades WHERE run_id = ? ORDER BY time DESC LIMIT ?", [run_id, limit])
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
        con.close()
        return {"run_id": run_id, "trades": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics/{run_id}")
def get_metrics(run_id: str):
    try:
        con = duckdb.connect(os.environ.get("MMRL_DUCKDB_PATH", "data/mmrl.duckdb"))
        cur = con.execute("SELECT key, value FROM metrics WHERE run_id = ?", [run_id])
        rows = cur.fetchall()
        con.close()
        return {"run_id": run_id, "metrics": {k: v for k, v in rows}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/run/{run_id}")
def get_run_db(run_id: str):
    try:
        con = duckdb.connect(os.environ.get("MMRL_DUCKDB_PATH", "data/mmrl.duckdb"))
        cur = con.execute("SELECT * FROM runs WHERE id = ?", [run_id])
        desc = cur.description
        row = cur.fetchone()
        con.close()
        if not row:
            raise HTTPException(status_code=404, detail="run not found")
        data = {desc[i][0]: row[i] for i in range(len(row))}
        # Attempt to enrich with MLflow info
        data.update(mlflow_info({"run_tag": data.get("experiment", "mmrl")}))
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# RQ job functions

@JOB_DURATION.time()
def _run_grid_job(job_id: str, cfg: Optional[Dict[str, Any]]):
    try:
        update_job(job_id, status="running", started_at=time.time())
        db_upsert_run({"id": job_id, "type": "grid", "experiment": (cfg or {}).get("run_tag", "mmrl"), "status": "running", "payload": cfg, "submitted_at": time.time()})
        run_with_config(["mmrl", "grid"], cfg)
        time.sleep(0.1)
        run_dir = get_latest_run_dir()
        info = mlflow_info(cfg or {})
        update_job(job_id, status="completed", finished_at=time.time(), run_dir=str(run_dir))
        db_upsert_run({"id": job_id, "type": "grid", "experiment": (cfg or {}).get("run_tag", "mmrl"), "run_dir": str(run_dir), "mlflow_run_id": info.get("mlflow_run_id"), "status": "completed", "payload": cfg, "finished_at": time.time()})
    except Exception as e:
        JOB_FAILURES.inc()
        update_job(job_id, status="failed", finished_at=time.time(), error=str(e))
        db_upsert_run({"id": job_id, "type": "grid", "experiment": (cfg or {}).get("run_tag", "mmrl"), "status": "failed", "payload": cfg})


@JOB_DURATION.time()
def _run_train_job(job_id: str, cfg: Optional[Dict[str, Any]]):
    try:
        update_job(job_id, status="running", started_at=time.time())
        db_upsert_run({"id": job_id, "type": "train", "experiment": (cfg or {}).get("run_tag", "mmrl"), "status": "running", "payload": cfg, "submitted_at": time.time()})
        run_with_config(["mmrl", "train"], cfg)
        info = mlflow_info(cfg or {})
        update_job(job_id, status="completed", finished_at=time.time())
        db_upsert_run({"id": job_id, "type": "train", "experiment": (cfg or {}).get("run_tag", "mmrl"), "status": "completed", "mlflow_run_id": info.get("mlflow_run_id"), "finished_at": time.time()})
    except Exception as e:
        JOB_FAILURES.inc()
        update_job(job_id, status="failed", finished_at=time.time(), error=str(e))
        db_upsert_run({"id": job_id, "type": "train", "experiment": (cfg or {}).get("run_tag", "mmrl"), "status": "failed", "payload": cfg})


@JOB_DURATION.time()
def _run_evaluate_job(job_id: str, cfg: Optional[Dict[str, Any]]):
    try:
        update_job(job_id, status="running", started_at=time.time())
        db_upsert_run({"id": job_id, "type": "evaluate", "experiment": (cfg or {}).get("run_tag", "mmrl"), "status": "running", "payload": cfg, "submitted_at": time.time()})
        run_with_config(["mmrl", "evaluate"], cfg)
        info = mlflow_info(cfg or {})
        update_job(job_id, status="completed", finished_at=time.time())
        db_upsert_run({"id": job_id, "type": "evaluate", "experiment": (cfg or {}).get("run_tag", "mmrl"), "status": "completed", "mlflow_run_id": info.get("mlflow_run_id"), "finished_at": time.time()})
    except Exception as e:
        JOB_FAILURES.inc()
        update_job(job_id, status="failed", finished_at=time.time(), error=str(e))
        db_upsert_run({"id": job_id, "type": "evaluate", "experiment": (cfg or {}).get("run_tag", "mmrl"), "status": "failed", "payload": cfg})


def _run_evaluate_multi_job(job_id: str, cfg: Optional[Dict[str, Any]]):
    try:
        update_job(job_id, status="running", started_at=time.time())
        # Reuse run_with_config to pass overrides
        run_with_config(["python3", "experiments/evaluate_multi_asset.py"], cfg)
        update_job(job_id, status="completed", finished_at=time.time())
    except Exception as e:
        update_job(job_id, status="failed", finished_at=time.time(), error=str(e))