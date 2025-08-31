import asyncio
import time
from datetime import UTC, datetime

import pytest

from planar.utils import asyncify, utc_now


async def test_asyncify_converts_sync_to_async():
    """Test that asyncify correctly converts a synchronous function to an asynchronous one."""

    def sync_function(x, y):
        return x + y

    async_function = asyncify(sync_function)

    # Check that the function is now a coroutine function
    assert asyncio.iscoroutinefunction(async_function)
    assert not asyncio.iscoroutinefunction(sync_function)

    # Check that it can be awaited
    result = await async_function(5, 3)
    assert result == 8


async def test_asyncify_with_args_and_kwargs():
    """Test that asyncify correctly passes positional and keyword arguments."""

    def complex_function(a, b, c=0, d=0):
        return a + b + c + d

    async_function = asyncify(complex_function)

    # Test with positional args only
    result1 = await async_function(1, 2)
    assert result1 == 3

    # Test with positional and keyword args
    result2 = await async_function(1, 2, c=3, d=4)
    assert result2 == 10


async def test_asyncify_preserves_exceptions():
    """Test that asyncify preserves exceptions raised by the wrapped function."""

    def failing_function():
        raise ValueError("Expected error")

    async_function = asyncify(failing_function)

    with pytest.raises(ValueError, match="Expected error"):
        await async_function()


async def test_asyncify_non_blocking():
    """Test that asyncify runs the function in a way that doesn't block the event loop."""
    # This counter will be incremented by a task running concurrently with our slow function
    counter = 0

    @asyncify
    def slow_function():
        time.sleep(0.5)  # This would block the event loop if not run in executor
        return counter

    # This task will increment the counter while the slow function is running
    async def increment_counter():
        nonlocal counter
        await asyncio.sleep(0.1)  # Short sleep to allow the slow function to start
        for _ in range(10):
            counter += 1
            await asyncio.sleep(0.01)  # Short sleep to yield control

    # Create increment task
    task = asyncio.create_task(increment_counter())

    # Run the async function
    assert counter == 0
    result = await slow_function()
    # If the event loop was blocked, the counter would be 0
    assert counter == 10
    assert result == 10

    await task


def test_raises_when_applied_to_async_function():
    """Test that asyncify raises an error when applied to an async function."""

    async def async_function():
        pass

    with pytest.raises(ValueError, match="Function is already async"):
        asyncify(async_function)


def test_utc_now_returns_naive_utc():
    """utc_now should return a naive datetime captured within two timestamps."""

    before = datetime.now(UTC).replace(tzinfo=None)
    result = utc_now()
    after = datetime.now(UTC).replace(tzinfo=None)

    assert result.tzinfo is None
    assert before <= result <= after
