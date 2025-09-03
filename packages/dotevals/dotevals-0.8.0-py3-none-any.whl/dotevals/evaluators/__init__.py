"""Evaluators for dotevals.

This package provides built-in evaluators and supports plugin evaluators
through Python entry points. Evaluators can be imported directly:

    from dotevals.evaluators import exact_match, numeric_match

Plugin evaluators are automatically discovered and can be imported the same way:

    from dotevals.evaluators import my_custom_evaluator  # From a plugin
"""

from typing import Any

from .base import evaluator, get_metadata
from .registry import registry

__all__ = ["evaluator", "get_metadata", "registry"]


def __getattr__(name: str) -> Any:
    """Dynamic attribute access for evaluators.

    This allows importing evaluators like:

        >>> from dotevals.evaluators import exact_match

    It will look up the evaluator in the registry, which includes
    both built-in and plugin evaluators.
    """
    evaluator = registry.get(name)
    if evaluator is not None:
        return evaluator

    # If not found, raise AttributeError with helpful message
    available = registry.list_evaluators()
    raise AttributeError(
        f"No evaluator named '{name}'. Available evaluators: {', '.join(available)}"
    )


def __dir__():
    """List available attributes including all registered evaluators."""
    return __all__ + registry.list_evaluators()
