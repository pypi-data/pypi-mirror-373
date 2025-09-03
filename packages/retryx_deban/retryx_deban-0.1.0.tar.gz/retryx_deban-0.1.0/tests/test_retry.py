import pytest
import asyncio
from retryx_deban import retry


def test_sync_retry():
    calls = {"count": 0}

    @retry(max_attempts=3, delay=0.1)
    def fail_then_succeed():
        calls["count"] += 1
        if calls["count"] < 2:
            raise ValueError("fail")
        return "success"

    assert fail_then_succeed() == "success"


@pytest.mark.asyncio
async def test_async_retry():
    calls = {"count": 0}

    @retry(max_attempts=3, delay=0.1)
    async def fail_then_succeed():
        calls["count"] += 1
        if calls["count"] < 2:
            raise ValueError("fail")
        return "success"

    result = await fail_then_succeed()
    assert result == "success"
