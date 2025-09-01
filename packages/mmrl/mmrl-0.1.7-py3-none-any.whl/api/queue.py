from __future__ import annotations
import os

# Optional imports: allow API to start without Redis/RQ installed
try:
    import redis  # type: ignore
except Exception:  # pragma: no cover
    redis = None  # type: ignore

try:
    from rq import Queue  # type: ignore
except Exception:  # pragma: no cover
    Queue = None  # type: ignore


def get_redis():
    if redis is None:
        raise RuntimeError("redis package is not installed; install optional 'api' extras or set up Docker compose")
    url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    return redis.from_url(url)


def get_queue(name: str = "mmrl-jobs"):
    if Queue is None:
        class _DummyQueue:
            def enqueue(self, *args, **kwargs):
                raise RuntimeError("rq package is not installed; install optional 'api' extras or use Docker compose")
        return _DummyQueue()
    return Queue(name, connection=get_redis())