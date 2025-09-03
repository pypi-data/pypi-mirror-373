"""Metrics for dotevals.

This package provides built-in metrics and supports plugin metrics
through Python entry points. Metrics can be imported directly:

    from dotevals.metrics import accuracy

Plugin metrics are automatically discovered and can be imported the same way:

    from dotevals.metrics import f1_score  # From a plugin
"""

from typing import Any

from .base import Metric, metric
from .base import registry as legacy_registry  # For backward compatibility
from .registry import registry as metric_registry

# Re-export the metric types and decorator
__all__ = ["Metric", "metric", "registry"]

# For backward compatibility, expose the old dict-like registry
registry = legacy_registry


def __getattr__(name: str) -> Any:
    """Dynamic attribute access for metrics.

    This allows importing metrics like:
        from dotevals.metrics import accuracy

    It will look up the metric in the registry, which includes
    both built-in and plugin metrics.
    """
    metric_func = metric_registry.get(name)
    if metric_func is not None:
        return metric_func

    # If not found, raise AttributeError with helpful message
    available = metric_registry.list_metrics()
    raise AttributeError(
        f"No metric named '{name}'. Available metrics: {', '.join(available)}"
    )


def __dir__():
    """List available attributes including all registered metrics."""
    return __all__ + metric_registry.list_metrics()
