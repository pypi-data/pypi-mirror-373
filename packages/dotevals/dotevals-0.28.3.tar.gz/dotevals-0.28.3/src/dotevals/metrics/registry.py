"""Registry for metric plugins."""

from collections.abc import Callable

__all__ = ["MetricRegistry", "registry"]


class MetricRegistry:
    """Registry for metric functions.

    This registry manages both built-in and plugin metrics,
    providing a centralized way to discover and access metrics.
    """

    def __init__(self):
        self._metrics: dict[str, Callable] = {}
        self._plugins_loaded = False

        # Register built-in metrics
        from .base import accuracy

        self.register("accuracy", accuracy)

    def register(self, name: str, metric: Callable) -> None:
        """Register a metric function.

        Args:
            name: Name to register the metric under
            metric: The metric function (typically returns a Metric callable)
        """
        self._metrics[name] = metric

    def get(self, name: str) -> Callable | None:
        """Get a metric by name.

        Args:
            name: Name of the metric

        Returns:
            The metric function or None if not found
        """
        # Load plugins on first access
        if not self._plugins_loaded:
            self.load_plugins()

        return self._metrics.get(name)

    def list_metrics(self) -> list[str]:
        """List all available metric names.

        Returns:
            List of registered metric names
        """
        # Load plugins on first access
        if not self._plugins_loaded:
            self.load_plugins()

        return sorted(self._metrics.keys())

    def load_plugins(self) -> None:
        """Load metric plugins from entry points.

        This method discovers and loads all metric plugins
        registered under the 'dotevals.metrics' entry point group.
        """
        if self._plugins_loaded:
            return

        self._plugins_loaded = True

        try:
            import importlib.metadata

            # Load all entry points in the dotevals.metrics group
            entry_points = importlib.metadata.entry_points()

            # Handle different Python versions
            metric_entries = []
            if hasattr(entry_points, "select"):
                # Python 3.10+
                metric_entries = list(entry_points.select(group="dotevals.metrics"))
            else:
                # Python 3.9 - entry_points is a dict-like object
                group = entry_points.get("dotevals.metrics")
                if group is not None:
                    metric_entries = list(group)

            for entry_point in metric_entries:
                try:
                    # Load the metric function
                    metric = entry_point.load()
                    # Register it with the name from entry point
                    self.register(entry_point.name, metric)
                except Exception as e:
                    # Log but don't fail if a plugin can't be loaded
                    import warnings

                    warnings.warn(
                        f"Failed to load metric plugin '{entry_point.name}': {e}"
                    )
        except ImportError:
            # importlib.metadata not available (shouldn't happen in Python 3.8+)
            pass


# Create singleton registry instance
registry = MetricRegistry()
