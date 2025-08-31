from __future__ import annotations
from pathlib import Path
from typing import Optional, Dict, Any, List
import os
import json
import duckdb
import pandas as pd


def db_path() -> str:
    return os.environ.get("MMRL_DUCKDB_PATH", "data/mmrl.duckdb")


def get_conn() -> duckdb.DuckDBPyConnection:
    path = db_path()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(path)


def init_db() -> None:
    con = get_conn()
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS runs (
          id TEXT PRIMARY KEY,
          type TEXT,
          experiment TEXT,
          run_dir TEXT,
          mlflow_run_id TEXT,
          status TEXT,
          payload TEXT,
          metrics TEXT,
          submitted_at DOUBLE,
          started_at DOUBLE,
          finished_at DOUBLE
        );
        """
    )
    # Migrate/add extra columns if missing
    cols = [r[1] for r in con.execute("PRAGMA table_info('runs')").fetchall()]
    if 'metadata' not in cols:
        con.execute("ALTER TABLE runs ADD COLUMN metadata TEXT;")
    if 'commit_hash' not in cols:
        con.execute("ALTER TABLE runs ADD COLUMN commit_hash TEXT;")
    if 'config_hash' not in cols:
        con.execute("ALTER TABLE runs ADD COLUMN config_hash TEXT;")

    con.execute(
        """
        CREATE TABLE IF NOT EXISTS metrics (
          run_id TEXT,
          experiment TEXT,
          key TEXT,
          value DOUBLE
        );
        """
    )
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS trades (
          run_id TEXT,
          time BIGINT,
          bid DOUBLE,
          ask DOUBLE,
          mid_price DOUBLE,
          inventory BIGINT,
          executed_bid DOUBLE,
          executed_ask DOUBLE,
          pnl DOUBLE,
          sigma DOUBLE
        );
        """
    )
    con.close()


def upsert_run(row: Dict[str, Any]) -> None:
    con = get_conn()
    con.execute("DELETE FROM runs WHERE id = ?", [row.get("id")])
    con.execute(
        "INSERT INTO runs (id,type,experiment,run_dir,mlflow_run_id,status,payload,metrics,submitted_at,started_at,finished_at,metadata,commit_hash,config_hash) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        [
            row.get("id"),
            row.get("type"),
            row.get("experiment"),
            row.get("run_dir"),
            row.get("mlflow_run_id"),
            row.get("status"),
            json.dumps(row.get("payload") or {}),
            json.dumps(row.get("metrics") or {}),
            row.get("submitted_at"),
            row.get("started_at"),
            row.get("finished_at"),
            json.dumps(row.get("metadata") or {}),
            row.get("commit_hash"),
            row.get("config_hash"),
        ],
    )
    con.close()


def list_runs(experiment: Optional[str] = None, start_ts: Optional[float] = None, end_ts: Optional[float] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    con = get_conn()
    query = "SELECT * FROM runs WHERE 1=1"
    params: List[Any] = []
    if experiment:
        query += " AND experiment = ?"
        params.append(experiment)
    if start_ts is not None:
        query += " AND submitted_at >= ?"
        params.append(start_ts)
    if end_ts is not None:
        query += " AND submitted_at <= ?"
        params.append(end_ts)
    query += " ORDER BY submitted_at DESC LIMIT ? OFFSET ?"
    params.append(limit)
    params.append(offset)
    cur = con.execute(query, params)
    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    for r in rows:
        for key in ("payload", "metrics", "metadata"):
            if isinstance(r.get(key), str):
                try:
                    r[key] = json.loads(r[key]) if r[key] else {}
                except Exception:
                    pass
    con.close()
    return rows


def count_runs(experiment: Optional[str] = None, start_ts: Optional[float] = None, end_ts: Optional[float] = None) -> int:
    con = get_conn()
    query = "SELECT COUNT(*) FROM runs WHERE 1=1"
    params: List[Any] = []
    if experiment:
        query += " AND experiment = ?"
        params.append(experiment)
    if start_ts is not None:
        query += " AND submitted_at >= ?"
        params.append(start_ts)
    if end_ts is not None:
        query += " AND submitted_at <= ?"
        params.append(end_ts)
    cur = con.execute(query, params)
    val = cur.fetchone()[0]
    con.close()
    return int(val)


def save_metrics(run_id: str, experiment: str, metrics: Dict[str, Any]) -> None:
    if not metrics:
        return
    rows = [(run_id, experiment, k, float(v)) for k, v in metrics.items() if isinstance(v, (int, float))]
    if not rows:
        return
    con = get_conn()
    con.executemany("INSERT INTO metrics (run_id, experiment, key, value) VALUES (?,?,?,?)", rows)
    con.close()


def save_trades(run_id: str, df: pd.DataFrame) -> None:
    if df is None or df.empty:
        return
    cols = [
        "time",
        "bid",
        "ask",
        "mid_price",
        "inventory",
        "executed_bid",
        "executed_ask",
        "pnl",
        "sigma",
    ]
    for c in cols:
        if c not in df.columns:
            df[c] = None
    con = get_conn()
    con.executemany(
        "INSERT INTO trades (run_id,time,bid,ask,mid_price,inventory,executed_bid,executed_ask,pnl,sigma) VALUES (?,?,?,?,?,?,?,?,?,?)",
        [
            (
                run_id,
                int(row["time"]) if row["time"] is not None else None,
                float(row["bid"]) if row["bid"] is not None else None,
                float(row["ask"]) if row["ask"] is not None else None,
                float(row["mid_price"]) if row["mid_price"] is not None else None,
                int(row["inventory"]) if row["inventory"] is not None else None,
                float(row["executed_bid"]) if row["executed_bid"] is not None else None,
                float(row["executed_ask"]) if row["executed_ask"] is not None else None,
                float(row["pnl"]) if row["pnl"] is not None else None,
                float(row["sigma"]) if row["sigma"] is not None else None,
            )
            for _, row in df.iterrows()
        ],
    )
    con.close()