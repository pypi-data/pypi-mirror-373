from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, Optional, List
import json
import time
import uuid

JOBS_ROOT = Path("results") / "jobs"
JOBS_ROOT.mkdir(parents=True, exist_ok=True)


def _job_path(job_id: str) -> Path:
    return JOBS_ROOT / f"{job_id}.json"


def create_job(job_type: str, payload: Optional[Dict[str, Any]] = None) -> str:
    job_id = uuid.uuid4().hex
    data = {
        "id": job_id,
        "type": job_type,
        "status": "pending",
        "submitted_at": time.time(),
        "payload": payload or {},
        "run_dir": None,
        "error": None,
    }
    _job_path(job_id).write_text(json.dumps(data))
    return job_id


def update_job(job_id: str, **updates: Any) -> None:
    p = _job_path(job_id)
    if not p.exists():
        return
    data = json.loads(p.read_text())
    data.update(updates)
    p.write_text(json.dumps(data))


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    p = _job_path(job_id)
    if not p.exists():
        return None
    return json.loads(p.read_text())


def list_jobs(limit: int = 50) -> List[Dict[str, Any]]:
    jobs = []
    for fp in sorted(JOBS_ROOT.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:limit]:
        try:
            jobs.append(json.loads(fp.read_text()))
        except Exception:
            continue
    return jobs