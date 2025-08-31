import os
import pytest

# These are smoke tests that require the API to be running separately.
# Skip if not set
API_URL = os.environ.get("MMRL_API_URL", None)

pytestmark = pytest.mark.skipif(API_URL is None, reason="API URL not set; set MMRL_API_URL to run smoke tests")


def test_health():
    import httpx
    r = httpx.get(f"{API_URL}/health", timeout=5)
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_jobs_list_schema():
    import httpx
    r = httpx.get(f"{API_URL}/jobs", timeout=5)
    assert r.status_code == 200
    assert "jobs" in r.json()