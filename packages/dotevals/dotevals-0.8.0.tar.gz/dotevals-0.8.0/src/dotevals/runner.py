"""Execution runners for dotevals evaluations."""

import asyncio
from typing import Any

import pytest

from dotevals.progress import MultiProgress


class Runner:
    """Base runner for dotevals evaluations.

    The Runner class handles all evaluation orchestration including:
    - Sequential and concurrent execution strategies
    - Fixture lifecycle management
    - Progress tracking and reporting
    - Result collection

    For resource management (model clients, database connections, etc.), use
    pytest fixtures with appropriate scopes (session, module, function).

    Examples:
        Direct usage:
        ```python
        runner = Runner(
            experiment_name="my_experiment",
            samples=100,
            concurrent=True
        )
        await runner.run_evaluations(evaluation_items)
        ```

        The Runner handles all orchestration logic internally, so subclasses
        typically don't need to override any methods.
    """

    def __init__(
        self,
        experiment_name: str | None = None,
        samples: int | None = None,
        storage: str | None = None,
        concurrent: bool = True,
        results_dict: dict[str, Any] | None = None,
    ) -> None:
        """Initialize runner with evaluation parameters.

        Args:
            experiment_name: Name of the experiment
            samples: Number of samples to evaluate
            storage: Storage backend path (e.g., 'json://.dotevals', 'sqlite://results.db')
            concurrent: Whether to run async evaluations concurrently
            results_dict: Optional dictionary to store evaluation results
        """
        self.experiment_name = experiment_name
        self.samples = samples
        self.storage = storage
        self.concurrent = concurrent
        self.results = results_dict if results_dict is not None else {}
        self.progress_manager = MultiProgress()

    async def run_evaluations(self, evaluation_items: list[pytest.Item]) -> None:
        """Run all evaluation items with common orchestration logic.

        This method provides the standard orchestration for running evaluations,
        handling both sequential and concurrent execution.

        Args:
            evaluation_items: List of pytest items representing evaluations
        """
        if not evaluation_items:
            return

        # Separate items by execution strategy
        sequential_items = []
        concurrent_items = []

        for item in evaluation_items:
            if self.concurrent and _is_async_evaluation(item):
                concurrent_items.append(item)
            else:
                sequential_items.append(item)

        # Start progress display
        total_items = len(sequential_items) + len(concurrent_items)
        self.progress_manager.start(total_items)

        try:
            # Run sequential items first
            for item in sequential_items:
                await self._run_single_evaluation(item)

            # Run concurrent items together
            if concurrent_items:
                tasks = []
                for item in concurrent_items:
                    task = asyncio.create_task(self._run_single_evaluation(item))
                    tasks.append(task)
                await asyncio.gather(*tasks)
        finally:
            self.progress_manager.finish()

    async def _run_single_evaluation(self, item: pytest.Item) -> None:
        """Execute a single evaluation item.

        This method handles the execution of individual evaluations.

        Args:
            item: The pytest Item representing a single evaluation
        """
        from dotevals.evaluation import Evaluation
        from dotevals.sessions import SessionManager

        eval_fn = item.function

        # Evaluation objects are required
        if not isinstance(eval_fn, Evaluation):
            raise TypeError(
                f"Expected Evaluation object, got {type(eval_fn).__name__}. "
                "Use @foreach or @batch decorators to create evaluations."
            )

        session_manager = SessionManager(
            evaluation_name=item.name,
            experiment_name=self.experiment_name,
            storage=self.storage,
        )

        result = await eval_fn(
            session_manager=session_manager,
            samples=self.samples,
            progress_manager=self.progress_manager,
        )

        self.results[item.name] = result


def _is_async_evaluation(item: pytest.Item) -> bool:
    """Check if an evaluation item is async.

    All evaluations are Evaluation objects, and we check the underlying
    eval_fn to determine concurrency strategy.
    """
    from dotevals.evaluation import Evaluation

    eval_fn = item.function

    if not isinstance(eval_fn, Evaluation):
        raise TypeError(
            f"Expected Evaluation object, got {type(eval_fn).__name__}. "
            "Use @foreach or @batch decorators to create evaluations."
        )

    # Check the underlying eval_fn
    return asyncio.iscoroutinefunction(eval_fn.eval_fn)
