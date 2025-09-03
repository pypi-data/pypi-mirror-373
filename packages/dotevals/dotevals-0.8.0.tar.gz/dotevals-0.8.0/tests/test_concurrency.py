"""Test the Tenacity-style concurrency API."""

import asyncio
import time
from unittest.mock import AsyncMock, Mock

import pytest

from dotevals.concurrency import Concurrency, adaptive, fixed, sequential


@pytest.mark.asyncio
async def test_fixed_concurrency_limits():
    """Test that fixed concurrency properly limits concurrent executions."""
    concurrency = Concurrency(fixed(2))
    currently_running = 0
    max_concurrent = 0

    async def simulate_work():
        nonlocal currently_running, max_concurrent
        await concurrency.acquire()
        try:
            currently_running += 1
            max_concurrent = max(max_concurrent, currently_running)
            await asyncio.sleep(0.01)
            currently_running -= 1
            return "done"
        finally:
            await concurrency.release()

    # Run 5 tasks with max concurrency of 2
    tasks = [simulate_work() for _ in range(5)]
    results = await asyncio.gather(*tasks)

    assert len(results) == 5
    assert all(r == "done" for r in results)
    assert max_concurrent <= 2


@pytest.mark.asyncio
async def test_sequential_execution():
    """Test that sequential strategy enforces one-at-a-time execution."""
    concurrency = Concurrency(sequential())
    execution_order = []

    async def task(task_id):
        await concurrency.acquire()
        try:
            execution_order.append(f"start_{task_id}")
            await asyncio.sleep(0.01)
            execution_order.append(f"end_{task_id}")
        finally:
            await concurrency.release()

    # Run tasks concurrently - sequential strategy should serialize them
    await asyncio.gather(task(1), task(2), task(3))

    # Check that tasks didn't overlap
    assert execution_order == [
        "start_1",
        "end_1",
        "start_2",
        "end_2",
        "start_3",
        "end_3",
    ]


@pytest.mark.asyncio
async def test_concurrency_wrapper():
    """Test wrapping a client with concurrency control."""
    mock_client = AsyncMock()
    mock_client.generate = AsyncMock(return_value="response")

    concurrency = Concurrency(fixed(2))
    wrapped_client = concurrency.wrap(mock_client)

    # Make concurrent calls
    tasks = [wrapped_client.generate(f"prompt_{i}") for i in range(3)]
    results = await asyncio.gather(*tasks)

    assert len(results) == 3
    assert all(r == "response" for r in results)
    assert mock_client.generate.call_count == 3


@pytest.mark.asyncio
async def test_concurrency_context_manager():
    """Test using Concurrency as a context manager."""
    strategy_mock = Mock()
    strategy_mock.reset = Mock()
    strategy_mock.acquire = AsyncMock()
    strategy_mock.release = AsyncMock()

    concurrency = Concurrency(strategy_mock)

    async with concurrency as c:
        assert c is concurrency
        # Use concurrency
        await c.acquire()
        await c.release()

    # Check reset was called on exit
    strategy_mock.reset.assert_called_once()


@pytest.mark.asyncio
async def test_concurrency_callbacks():
    """Test before/after callbacks."""
    before_acquire_called = []
    after_acquire_called = []
    before_release_called = []
    after_release_called = []

    def before_acquire(strategy):
        before_acquire_called.append(strategy)

    def after_acquire(strategy):
        after_acquire_called.append(strategy)

    def before_release(strategy, error):
        before_release_called.append((strategy, error))

    def after_release(strategy, error):
        after_release_called.append((strategy, error))

    concurrency = Concurrency(
        fixed(1),
        before_acquire=before_acquire,
        after_acquire=after_acquire,
        before_release=before_release,
        after_release=after_release,
    )

    await concurrency.acquire()
    await concurrency.release()

    assert len(before_acquire_called) == 1
    assert len(after_acquire_called) == 1
    assert len(before_release_called) == 1
    assert len(after_release_called) == 1


@pytest.mark.asyncio
async def test_adaptive_error_backoff():
    """Test that adaptive strategy backs off on errors."""
    strategy = adaptive(
        initial=5, min=1, max=10, error_backoff=0.5, adaptation_interval=0.01
    )

    # Acquire some slots
    await strategy.acquire()
    initial_concurrency = strategy.current

    # Release with error - should reduce concurrency
    await strategy.release(error=Exception("test error"))

    # Wait for adaptation interval to pass
    await asyncio.sleep(0.02)

    # Force adaptation
    await strategy._maybe_adapt()

    assert strategy.current < initial_concurrency
    assert strategy.current >= strategy.min_concurrency


@pytest.mark.asyncio
async def test_wrapper_error_propagation():
    """Test that wrapped client properly propagates errors."""
    mock_client = AsyncMock()
    mock_client.generate = AsyncMock(side_effect=ValueError("test error"))

    concurrency = Concurrency(fixed(1))
    wrapped_client = concurrency.wrap(mock_client)

    with pytest.raises(ValueError, match="test error"):
        await wrapped_client.generate("test")

    # Verify the concurrency was still released on error
    # (We can acquire again immediately)
    await concurrency.acquire()
    await concurrency.release()


@pytest.mark.asyncio
async def test_fixed_strategy_reset():
    """Test that fixed strategy properly resets."""
    strategy = fixed(2)

    # Acquire all slots
    await strategy.acquire()
    await strategy.acquire()

    # Reset should free up slots
    strategy.reset()

    # Should be able to acquire again
    await strategy.acquire()
    await strategy.acquire()


@pytest.mark.asyncio
async def test_adaptive_throughput_tracking():
    """Test that adaptive strategy tracks throughput."""
    strategy = adaptive(initial=2, max=5)

    # Simulate some completions
    for _ in range(5):
        await strategy.acquire()
        await asyncio.sleep(0.01)
        await strategy.release()

    # Check that completion times were recorded
    assert len(strategy.completion_times) > 0

    # Reset and check state is cleared
    strategy.reset()
    assert len(strategy.completion_times) == 0
    assert strategy.error_count == 0


@pytest.mark.asyncio
async def test_adaptive_concurrency_adaptation():
    """Test adaptive concurrency strategy adaptation logic."""
    strategy = adaptive(
        initial=2,
        min=1,
        max=10,
        increase_threshold=0.95,
        decrease_threshold=0.85,
        adaptation_interval=0.01,
    )

    # Test initial state
    assert strategy.current == 2

    # Simulate some completions
    await strategy.acquire()
    await strategy.release(error=None)

    # Add completion times
    strategy.completion_times = [time.time() - 1, time.time()]

    # Force adaptation
    strategy.last_adaptation = time.time() - 3
    await strategy._maybe_adapt()

    # Should still be within bounds
    assert strategy.current >= 1
    assert strategy.current <= 10


@pytest.mark.asyncio
async def test_adaptive_active_tracking():
    """Test active count tracking in adaptive strategy."""
    strategy = adaptive(initial=5)

    assert strategy.active_count == 0

    # Acquire some slots
    await strategy.acquire()
    assert strategy.active_count == 1

    await strategy.acquire()
    assert strategy.active_count == 2

    # Release
    await strategy.release()
    assert strategy.active_count == 1

    await strategy.release()
    assert strategy.active_count == 0


@pytest.mark.asyncio
async def test_adaptive_adaptation_interval():
    """Test that adaptation respects interval."""
    strategy = adaptive(
        initial=3,
        adaptation_interval=1.0,
    )

    # First adaptation
    strategy.last_adaptation = time.time() - 2
    strategy.completion_times = [time.time() - 1, time.time()]
    await strategy._maybe_adapt()

    last_adapt_time = strategy.last_adaptation

    # Try again immediately - should not adapt
    await strategy._maybe_adapt()

    # Should not have changed
    assert strategy.last_adaptation == last_adapt_time


@pytest.mark.asyncio
async def test_fixed_acquire_release():
    """Test fixed strategy acquire/release."""
    strategy = fixed(2)

    # Should be able to acquire up to limit
    await strategy.acquire()
    await strategy.acquire()

    # Release to make room
    await strategy.release()

    # Can acquire again
    await strategy.acquire()
    await strategy.release()
    await strategy.release()


def test_sequential_strategy_properties():
    """Test sequential strategy initialization."""
    strategy = sequential()

    # Sequential uses a lock for serialization
    assert hasattr(strategy, "lock")
    assert isinstance(strategy.lock, asyncio.Lock)


def test_concurrency_edge_cases():
    """Test edge cases in concurrency strategies."""
    # Zero workers
    strategy = fixed(0)
    assert strategy.semaphore._value == 0

    # Large number
    strategy = fixed(1000)
    assert strategy.semaphore._value == 1000

    # Adaptive with same min/max
    strategy = adaptive(initial=5, min=5, max=5)
    assert strategy.current == 5
    assert strategy.min_concurrency == 5
    assert strategy.max_concurrency == 5


@pytest.mark.asyncio
async def test_concurrency_error_propagation():
    """Test error propagation in concurrent execution."""

    # Create tasks with errors
    async def failing_task():
        await asyncio.sleep(0.01)
        raise ValueError("Task failed")

    async def successful_task():
        await asyncio.sleep(0.01)
        return "success"

    tasks = [failing_task(), successful_task()]

    # Run with error handling
    outcomes = await asyncio.gather(*tasks, return_exceptions=True)

    errors = [o for o in outcomes if isinstance(o, Exception)]
    results = [o for o in outcomes if not isinstance(o, Exception)]

    assert len(errors) == 1
    assert len(results) == 1
    assert str(errors[0]) == "Task failed"
    assert results[0] == "success"
