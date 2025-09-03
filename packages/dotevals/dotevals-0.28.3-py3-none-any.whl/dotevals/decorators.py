"""
Decorators for evaluation functions.
"""

from collections.abc import Callable, Iterable
from typing import Any, TypeAlias

import pytest

from dotevals.evaluation import Evaluation

# Type aliases
ColumnSpec: TypeAlias = str
DatasetValue: TypeAlias = str | int | float | bool | None | dict | list
DatasetRow: TypeAlias = (
    tuple[DatasetValue, ...]
    | list[DatasetValue]
    | dict[str, DatasetValue]
    | DatasetValue
)


class ForEach:
    """Evaluator that processes each dataset item individually."""

    def __call__(
        self,
        column_spec: ColumnSpec,
        dataset: Iterable[DatasetRow],
    ) -> Callable[[Callable], Callable]:
        """Create decorator for evaluation functions."""
        return create_decorator(
            "foreach",
            column_spec,
            dataset,
        )

    def __getattr__(self, dataset_name: str) -> Callable:
        """Support dataset access via attribute syntax."""
        # Avoid conflicts with special methods that tools might probe for
        if dataset_name.startswith("__") and dataset_name.endswith("__"):
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{dataset_name}'"
            )
        return create_dataset_decorator("foreach", dataset_name)


foreach = ForEach()


class Batch:
    """Evaluator that processes dataset items in batches."""

    def __call__(
        self,
        column_spec: ColumnSpec,
        dataset: Iterable[DatasetRow],
        *,
        batch_size: int | None = None,
    ) -> Callable[[Callable], Callable]:
        """Create decorator for evaluation functions."""

        return create_decorator(
            "batch",
            column_spec,
            dataset,
            batch_size=batch_size,
        )

    def __getattr__(self, dataset_name: str) -> Callable:
        """Support dataset access via attribute syntax."""
        # Avoid conflicts with special methods that tools might probe for
        if dataset_name.startswith("__") and dataset_name.endswith("__"):
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{dataset_name}'"
            )
        return create_dataset_decorator("batch", dataset_name)


def create_decorator(
    executor_type: str,
    column_spec: ColumnSpec,
    dataset: Iterable[DatasetRow],
    **kwargs: Any,
) -> Callable[[Callable], Evaluation]:
    """Create a decorator for evaluation functions.

    Args:
        executor_type: Type of executor to use ("foreach" or "batch")
        column_spec: Comma-separated list of column names
        dataset: Dataset to evaluate on
        **kwargs: Configuration kwargs to pass to the executor (e.g., batch_size)

    Returns:
        Decorator function that returns an Evaluation
    """

    def decorator(eval_fn: Callable) -> Evaluation:
        # Mark for pytest
        eval_fn = pytest.mark.dotevals(eval_fn)  # type: ignore

        # Create and return the evaluation
        return Evaluation(
            eval_fn=eval_fn,
            dataset=dataset,
            executor_name=executor_type,
            column_spec=column_spec,
            executor_kwargs=kwargs,
        )

    return decorator


batch = Batch()


def create_dataset_decorator(
    executor_type: str,
    dataset_name: str,
    **kwargs: Any,
) -> Callable:
    """Create a decorator for dataset attribute access.

    Args:
        executor_type: Type of executor to use ("foreach" or "batch")
        dataset_name: Name of the dataset
        **kwargs: Configuration kwargs to pass to the executor (e.g., batch_size)

    Returns:
        Dataset decorator function
    """

    def dataset_decorator(
        split: str | None = None, **dataset_kwargs: Any
    ) -> Callable[[Callable], Callable]:
        from dotevals.datasets import registry

        # Extract batch_size if present
        batch_size = dataset_kwargs.pop("batch_size", None)

        dataset_class = registry.get_dataset_class(dataset_name)
        dataset_instance = (
            dataset_class(split, **dataset_kwargs)
            if split is not None
            else dataset_class(**dataset_kwargs)
        )
        column_spec = ",".join(dataset_class.columns)

        # Add batch_size to kwargs if it was provided
        if batch_size is not None:
            kwargs["batch_size"] = batch_size

        return create_decorator(executor_type, column_spec, dataset_instance, **kwargs)

    dataset_decorator._dataset_name = dataset_name  # type: ignore
    return dataset_decorator


def __getattr__(name: str) -> Any:
    """Dynamic attribute access for executor-based decorators.

    This allows importing decorators from plugins like:
        >>> from dotevals import async_batch  # If plugin installed

    It checks if there's a registered executor with this name and if so,
    tries to import the corresponding decorator from the plugin package.
    """
    # Check if there's an executor registered with this name
    from dotevals.executors.registry import executor_registry

    executor = executor_registry.get(name)
    if executor is not None:
        # Convention: plugins should provide a decorator with the same name as the executor
        package_name = f"dotevals_{name}"  # e.g., dotevals_async_batch

        import importlib

        try:
            package = importlib.import_module(package_name)
            if hasattr(package, name):
                return getattr(package, name)
            else:
                raise AttributeError(
                    f"Executor '{name}' is registered but package '{package_name}' "
                    f"does not provide a '{name}' decorator"
                )
        except ImportError:
            raise AttributeError(
                f"Executor '{name}' is registered but could not import decorator '{name}' "
                f"from package '{package_name}'. The package may not follow the expected "
                f"naming convention or may not export the decorator."
            )

    # Default behavior - attribute not found
    raise AttributeError(f"module 'dotevals.decorators' has no attribute '{name}'")
