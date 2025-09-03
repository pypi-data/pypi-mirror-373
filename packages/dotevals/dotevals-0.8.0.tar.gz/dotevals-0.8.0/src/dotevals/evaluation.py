"""Evaluation for dotevals."""

import functools
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import Any

from dotevals.executors.batch import BatchExecutor
from dotevals.executors.foreach import ForEachExecutor
from dotevals.executors.registry import executor_registry
from dotevals.progress import BaseProgressManager
from dotevals.sessions import SessionManager
from dotevals.summary import EvaluationSummary


@dataclass
class Evaluation:
    """Represents an evaluation that can be executed.

    This class encapsulates all the information needed to execute an evaluation,
    making the evaluation pipeline explicit and type-safe.
    """

    eval_fn: Callable
    dataset: Iterable
    executor_name: str
    column_spec: str
    column_names: list[str] = field(init=False)
    executor_kwargs: dict[str, Any] = field(default_factory=dict)
    resolved_fixtures: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize derived fields."""
        self.column_names = [col.strip() for col in self.column_spec.split(",")]
        # Preserve the original function's metadata
        functools.update_wrapper(self, self.eval_fn)

    async def __call__(
        self,
        session_manager: SessionManager,
        samples: int | None = None,
        progress_manager: BaseProgressManager | None = None,
        **runtime_kwargs: Any,
    ) -> EvaluationSummary:
        """Execute the evaluation.

        This method makes Evaluation callable, allowing it to be used
        transparently with pytest and other testing frameworks.
        """
        all_kwargs = {**self.resolved_fixtures, **runtime_kwargs}

        executor = self._get_executor()

        return await executor.execute(
            self,
            session_manager,
            samples=samples,
            progress_manager=progress_manager,
            **all_kwargs,
        )

    def _get_executor(self):
        """Get the executor instance."""
        executor = executor_registry.get(self.executor_name)
        if executor is None:
            # Fall back to built-in executors
            if self.executor_name == "foreach":
                executor = ForEachExecutor()
            elif self.executor_name == "batch":
                executor = BatchExecutor()
            else:
                raise RuntimeError(f"Unknown executor type: {self.executor_name}")
        return executor
