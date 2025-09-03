"""Registry for evaluator plugins."""

from collections.abc import Callable

__all__ = ["EvaluatorRegistry", "registry"]


class EvaluatorRegistry:
    """Registry for evaluator functions.

    This registry manages both built-in and plugin evaluators,
    providing a centralized way to discover and access evaluators.
    """

    def __init__(self):
        self._evaluators: dict[str, Callable] = {}
        self._plugins_loaded = False

        # Register built-in evaluators
        from .ast_evaluation import ast_evaluation
        from .base import exact_match, numeric_match, valid_json

        self.register("exact_match", exact_match)
        self.register("numeric_match", numeric_match)
        self.register("valid_json", valid_json)
        self.register("ast_evaluation", ast_evaluation)

    def register(self, name: str, evaluator: Callable) -> None:
        """Register an evaluator function.

        Args:
            name: Name to register the evaluator under
            evaluator: The evaluator function
        """
        self._evaluators[name] = evaluator

    def get(self, name: str) -> Callable | None:
        """Get an evaluator by name.

        Args:
            name: Name of the evaluator

        Returns:
            The evaluator function or None if not found
        """
        # Load plugins on first access
        if not self._plugins_loaded:
            self.load_plugins()

        return self._evaluators.get(name)

    def list_evaluators(self) -> list[str]:
        """List all available evaluator names.

        Returns:
            List of registered evaluator names
        """
        # Load plugins on first access
        if not self._plugins_loaded:
            self.load_plugins()

        return sorted(self._evaluators.keys())

    def load_plugins(self) -> None:
        """Load evaluator plugins from entry points.

        This method discovers and loads all evaluator plugins
        registered under the 'dotevals.evaluators' entry point group.
        """
        if self._plugins_loaded:
            return

        self._plugins_loaded = True

        try:
            import importlib.metadata

            # Load all entry points in the dotevals.evaluators group
            entry_points = importlib.metadata.entry_points()

            # Handle different Python versions
            evaluator_entries = []
            if hasattr(entry_points, "select"):
                # Python 3.10+
                evaluator_entries = list(
                    entry_points.select(group="dotevals.evaluators")
                )
            else:
                # Python 3.9 - entry_points is a dict-like object
                group = entry_points.get("dotevals.evaluators")
                if group is not None:
                    evaluator_entries = list(group)

            for entry_point in evaluator_entries:
                try:
                    # Load the evaluator function
                    evaluator = entry_point.load()
                    # Register it with the name from entry point
                    self.register(entry_point.name, evaluator)
                except Exception as e:
                    # Log but don't fail if a plugin can't be loaded
                    import warnings

                    warnings.warn(
                        f"Failed to load evaluator plugin '{entry_point.name}': {e}"
                    )
        except ImportError:
            # importlib.metadata not available (shouldn't happen in Python 3.8+)
            pass


# Create singleton registry instance
registry = EvaluatorRegistry()
