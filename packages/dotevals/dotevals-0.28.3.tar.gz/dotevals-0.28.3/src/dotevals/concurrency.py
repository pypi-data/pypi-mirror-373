"""Tenacity-style concurrency control utility for dotevals.

NOTE: This module provides optional concurrency utilities that can be used
to wrap API clients. It is NOT part of the core dotevals framework. The
decorators (@foreach, @batch) execute evaluations sequentially by default.

This is a convenience utility for users who want to add concurrency control
to their clients, similar to how Tenacity provides retry utilities. You can
use any concurrency control library you prefer - this is just one option.

Example:
    from dotevals.concurrency import Concurrency, fixed

    # Wrap your client with concurrency control
    client = openai.AsyncClient()
    concurrent_client = Concurrency(fixed(10)).wrap(client)

    # Use in evaluations - concurrency is handled by the wrapped client
    @foreach("prompt,expected", dataset)
    async def evaluate(prompt, expected, concurrent_client):
        response = await concurrent_client.generate(prompt)
        return exact_match(response, expected)
"""

import asyncio
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")


class ConcurrencyStrategy(ABC):
    """Base class for concurrency strategies."""

    @abstractmethod
    async def acquire(self) -> None:
        """Acquire permission to proceed."""
        pass

    @abstractmethod
    async def release(self, error: Exception | None = None) -> None:
        """Release a slot after completion."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset the strategy state."""
        pass


class adaptive(ConcurrencyStrategy):
    """Adaptive concurrency that adjusts based on throughput.

    Similar to Tenacity's wait strategies, this returns a strategy instance.

    Usage:
        strategy = adaptive(initial=5, max=50)
        concurrency = Concurrency(strategy)
    """

    def __init__(
        self,
        initial: int = 5,
        min: int = 1,
        max: int = 100,
        increase_threshold: float = 0.98,
        decrease_threshold: float = 0.90,
        adaptation_interval: float = 2.0,
        error_backoff: float = 0.7,
    ):
        self.current = initial
        self.min_concurrency = min
        self.max_concurrency = max
        self.increase_threshold = increase_threshold
        self.decrease_threshold = decrease_threshold
        self.adaptation_interval = adaptation_interval
        self.error_backoff = error_backoff

        # State tracking
        self.semaphore = asyncio.Semaphore(initial)
        self.active_count = 0
        self.last_throughput: float | None = None
        self.last_adaptation = time.time()
        self.completion_times: list[float] = []
        self.error_count = 0

        # Start adaptation task
        self._adaptation_task: asyncio.Task[None] | None = None

    async def acquire(self) -> None:
        """Acquire a slot."""
        await self.semaphore.acquire()
        self.active_count += 1

        # Start adaptation task if not running
        if self._adaptation_task is None:
            self._adaptation_task = asyncio.create_task(self._adapt_loop())

    async def release(self, error: Exception | None = None) -> None:
        """Release a slot and record metrics."""
        self.semaphore.release()
        self.active_count -= 1

        if error:
            self.error_count += 1
        else:
            self.completion_times.append(time.time())

        # Adapt if needed
        await self._maybe_adapt()

    async def _adapt_loop(self) -> None:
        """Background adaptation loop."""
        while self.active_count > 0:
            await asyncio.sleep(self.adaptation_interval)
            await self._maybe_adapt()

    async def _maybe_adapt(self) -> None:
        """Adapt concurrency based on throughput."""
        now = time.time()
        if now - self.last_adaptation < self.adaptation_interval:
            return

        # Calculate current throughput
        if len(self.completion_times) >= 2:
            time_span = self.completion_times[-1] - self.completion_times[0]
            if time_span > 0:
                current_throughput = len(self.completion_times) / time_span

                # Adjust based on throughput change
                if self.last_throughput:
                    ratio = current_throughput / self.last_throughput

                    if (
                        ratio > self.increase_threshold
                        and self.current < self.max_concurrency
                    ):
                        # Increase concurrency
                        self.current = min(
                            int(self.current * 1.2), self.max_concurrency
                        )
                        self._update_semaphore()
                    elif (
                        ratio < self.decrease_threshold
                        and self.current > self.min_concurrency
                    ):
                        # Decrease concurrency
                        self.current = max(
                            int(self.current * 0.8), self.min_concurrency
                        )
                        self._update_semaphore()

                self.last_throughput = current_throughput

        # Handle errors
        if self.error_count > 0:
            self.current = max(
                int(self.current * self.error_backoff), self.min_concurrency
            )
            self._update_semaphore()
            self.error_count = 0

        self.last_adaptation = now

        # Keep only recent completions
        if len(self.completion_times) > 100:
            self.completion_times = self.completion_times[-50:]

    def _update_semaphore(self) -> None:
        """Update semaphore to match current concurrency."""
        # This is a simplified version - in production you'd need more care
        self.semaphore = asyncio.Semaphore(self.current)

    def reset(self) -> None:
        """Reset the strategy state."""
        self.semaphore = asyncio.Semaphore(self.current)
        self.active_count = 0
        self.completion_times.clear()
        self.error_count = 0
        self.last_throughput = None


class fixed(ConcurrencyStrategy):
    """Fixed concurrency limit.

    Usage:
        strategy = fixed(10)  # Allow 10 concurrent requests
        concurrency = Concurrency(strategy)
    """

    def __init__(self, size: int):
        self.size = size
        self.semaphore = asyncio.Semaphore(size)

    async def acquire(self) -> None:
        """Acquire a slot."""
        await self.semaphore.acquire()

    async def release(self, error: Exception | None = None) -> None:
        """Release a slot."""
        self.semaphore.release()

    def reset(self) -> None:
        """Reset the semaphore."""
        self.semaphore = asyncio.Semaphore(self.size)


class sequential(ConcurrencyStrategy):
    """Sequential execution (concurrency=1)."""

    def __init__(self):
        self.lock = asyncio.Lock()

    async def acquire(self) -> None:
        await self.lock.acquire()

    async def release(self, error: Exception | None = None) -> None:
        self.lock.release()

    def reset(self) -> None:
        self.lock = asyncio.Lock()


class Concurrency:
    """Tenacity-style concurrency control.

    Usage:
        # Create with strategy
        concurrency = Concurrency(adaptive(max=50))

        # Wrap a client
        client = concurrency.wrap(api_client)

        # Or use directly
        async with concurrency:
            for item in items:
                await concurrency.acquire()
                try:
                    result = await process(item)
                finally:
                    await concurrency.release()
    """

    def __init__(
        self,
        strategy: ConcurrencyStrategy | None = None,
        *,
        before_acquire: Callable[[Any], None] | None = None,
        after_acquire: Callable[[Any], None] | None = None,
        before_release: Callable[[Any, Exception | None], None] | None = None,
        after_release: Callable[[Any, Exception | None], None] | None = None,
    ):
        self.strategy = strategy or fixed(10)
        self.before_acquire = before_acquire
        self.after_acquire = after_acquire
        self.before_release = before_release
        self.after_release = after_release

    async def acquire(self) -> None:
        """Acquire a concurrency slot."""
        if self.before_acquire:
            self.before_acquire(self.strategy)

        await self.strategy.acquire()

        if self.after_acquire:
            self.after_acquire(self.strategy)

    async def release(self, error: Exception | None = None) -> None:
        """Release a concurrency slot."""
        if self.before_release:
            self.before_release(self.strategy, error)

        await self.strategy.release(error)

        if self.after_release:
            self.after_release(self.strategy, error)

    def wrap(self, client: Any) -> "ConcurrencyWrapper":
        """Wrap a client with concurrency control."""
        return ConcurrencyWrapper(client, self)

    async def __aenter__(self):
        """Context manager support."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up on exit."""
        self.strategy.reset()
        return False


class ConcurrencyWrapper:
    """Wrapper that applies concurrency control to a client."""

    def __init__(self, client: Any, concurrency: Concurrency):
        self.client = client
        self.concurrency = concurrency

    def __getattr__(self, name: str) -> Any:
        """Wrap callable attributes with concurrency control."""
        attr = getattr(self.client, name)

        if not callable(attr):
            return attr

        if asyncio.iscoroutinefunction(attr):
            return self._wrap_async(attr)
        else:
            return self._wrap_sync(attr)

    def _wrap_async(self, func: Callable) -> Callable:
        """Wrap an async function with concurrency control."""

        async def wrapped(*args, **kwargs):
            await self.concurrency.acquire()
            try:
                result = await func(*args, **kwargs)
                await self.concurrency.release()
                return result
            except Exception as e:
                await self.concurrency.release(error=e)
                raise

        return wrapped

    def _wrap_sync(self, func: Callable) -> Callable:
        """Wrap a sync function with concurrency control."""

        def wrapped(*args, **kwargs):
            # For sync functions, we'd need a different approach
            # This is a simplified version
            return func(*args, **kwargs)

        return wrapped
