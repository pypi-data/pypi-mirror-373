import numpy as np
from utils.metrics import sharpe, max_drawdown, hit_rate


def test_metrics_basic():
    r = np.array([1, -1, 1, -1], dtype=float)
    s = sharpe(r)
    assert np.isfinite(s)
    dd = max_drawdown(np.cumsum(r))
    assert dd <= 0
    hr = hit_rate(r)
    assert 0 <= hr <= 1