"""Registry for evaluation executor plugins."""

import importlib.metadata

from .base import Executor


class ExecutorRegistry:
    """Registry for evaluation executor plugins."""

    def __init__(self) -> None:
        self._executors: dict[str, Executor] = {}
        self._discovered = False

    def register(self, name: str, executor: Executor) -> None:
        """Register an executor plugin."""
        self._executors[name] = executor

    def get(self, name: str) -> Executor | None:
        """Get an executor by name."""
        self.discover_plugins()
        return self._executors.get(name)

    def discover_plugins(self) -> None:
        """Auto-discover executor plugins via entry points."""
        if self._discovered:
            return

        # Discover from entry points
        try:
            entry_points = importlib.metadata.entry_points()
            if hasattr(entry_points, "select"):
                # Python 3.10+
                executor_entry_points = list(
                    entry_points.select(group="dotevals.executors")
                )
            else:
                # Python 3.9
                group = entry_points.get("dotevals.executors")
                executor_entry_points = list(group) if group else []

            for entry_point in executor_entry_points:
                try:
                    executor_class = entry_point.load()
                    executor = executor_class()
                    self.register(entry_point.name, executor)
                except Exception as e:
                    print(f"Failed to load executor {entry_point.name}: {e}")
        except Exception:
            # If entry points fail, just continue with built-in executors
            pass

        self._discovered = True


# Global registry instance
executor_registry = ExecutorRegistry()
