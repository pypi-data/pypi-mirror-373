"""Tests for executor registry and plugin loading."""


def test_executor_registry_builtin_executors():
    """Test that built-in executors are registered."""
    from dotevals.executors.registry import executor_registry

    # Check built-in executors are registered
    assert executor_registry.get("foreach") is not None
    assert executor_registry.get("batch") is not None


def test_executor_registry_get_nonexistent():
    """Test getting non-existent executor returns None."""
    from dotevals.executors.registry import executor_registry

    assert executor_registry.get("nonexistent") is None


def test_executor_registry_register():
    """Test registering a custom executor."""
    from dotevals.executors.base import Executor
    from dotevals.executors.registry import executor_registry

    class CustomExecutor(Executor):
        @property
        def name(self):
            return "custom"

        def _execute_sync(self, eval_fn, dataset, column_names, samples, **kwargs):
            pass

        async def _execute_async(
            self, eval_fn, dataset, column_names, samples, **kwargs
        ):
            pass

        def execute(self, eval_fn, dataset, column_names, samples, **kwargs):
            pass

    custom_executor = CustomExecutor()
    executor_registry.register("custom", custom_executor)

    assert executor_registry.get("custom") is custom_executor


def test_executor_registry_plugin_discovery(monkeypatch):
    """Test loading executors from entry points."""
    import importlib.metadata
    from unittest.mock import MagicMock, Mock

    from dotevals.executors.base import Executor
    from dotevals.executors.registry import executor_registry

    # Create a mock executor class
    class PluginExecutor(Executor):
        @property
        def name(self):
            return "plugin_executor"

        def _execute_sync(self, eval_fn, dataset, column_names, samples, **kwargs):
            pass

        async def _execute_async(
            self, eval_fn, dataset, column_names, samples, **kwargs
        ):
            pass

        def execute(self, eval_fn, dataset, column_names, samples, **kwargs):
            pass

    # Mock entry point
    mock_entry_point = Mock()
    mock_entry_point.name = "plugin_executor"
    mock_entry_point.load.return_value = PluginExecutor

    # Mock entry_points() to return our mock entry point
    mock_entry_points = MagicMock()

    # Handle both Python 3.10+ and 3.9 styles
    if hasattr(importlib.metadata.entry_points(), "select"):
        # Python 3.10+ style
        mock_entry_points.select.return_value = [mock_entry_point]
    else:
        # Python 3.9 style
        mock_entry_points.get.return_value = [mock_entry_point]

    monkeypatch.setattr(importlib.metadata, "entry_points", lambda: mock_entry_points)

    # Force discovery
    executor_registry._discovered = False
    executor_registry.discover_plugins()

    # Check that the plugin was loaded
    plugin_executor = executor_registry.get("plugin_executor")
    assert plugin_executor is not None
    assert isinstance(plugin_executor, PluginExecutor)


def test_executor_registry_plugin_error_handling(monkeypatch, capsys):
    """Test that plugin loading errors are handled gracefully."""
    import importlib.metadata
    from unittest.mock import MagicMock, Mock

    from dotevals.executors.registry import executor_registry

    # Mock entry point that fails to load
    mock_entry_point = Mock()
    mock_entry_point.name = "broken_executor"
    mock_entry_point.load.side_effect = ImportError("Failed to load plugin")

    # Mock entry_points()
    mock_entry_points = MagicMock()

    if hasattr(importlib.metadata.entry_points(), "select"):
        mock_entry_points.select.return_value = [mock_entry_point]
    else:
        mock_entry_points.get.return_value = [mock_entry_point]

    monkeypatch.setattr(importlib.metadata, "entry_points", lambda: mock_entry_points)

    # Force discovery
    executor_registry._discovered = False
    executor_registry.discover_plugins()

    # Check that error was printed
    captured = capsys.readouterr()
    assert "Failed to load executor broken_executor" in captured.out

    # Plugin should not be registered
    assert executor_registry.get("broken_executor") is None


def test_executor_registry_python39_compatibility(monkeypatch):
    """Test plugin loading on Python 3.9 (no select method)."""
    import importlib.metadata
    from unittest.mock import MagicMock, Mock

    from dotevals.executors.base import Executor
    from dotevals.executors.registry import executor_registry

    # Create a mock executor class
    class OldStyleExecutor(Executor):
        @property
        def name(self):
            return "oldstyle_executor"

        def _execute_sync(self, eval_fn, dataset, column_names, samples, **kwargs):
            pass

        async def _execute_async(
            self, eval_fn, dataset, column_names, samples, **kwargs
        ):
            pass

        def execute(self, eval_fn, dataset, column_names, samples, **kwargs):
            pass

    # Mock entry point
    mock_entry_point = Mock()
    mock_entry_point.name = "oldstyle_executor"
    mock_entry_point.load.return_value = OldStyleExecutor

    # Mock entry_points() in Python 3.9 style (dict-like)
    mock_entry_points = MagicMock()
    # Ensure we don't have select method to simulate Python 3.9
    if hasattr(mock_entry_points, "select"):
        delattr(mock_entry_points, "select")
    mock_entry_points.get.return_value = [mock_entry_point]

    monkeypatch.setattr(importlib.metadata, "entry_points", lambda: mock_entry_points)

    # Force discovery
    executor_registry._discovered = False
    executor_registry.discover_plugins()

    # Check that the plugin was loaded
    plugin_executor = executor_registry.get("oldstyle_executor")
    assert plugin_executor is not None
    assert isinstance(plugin_executor, OldStyleExecutor)


def test_executor_registry_no_entries(monkeypatch):
    """Test plugin discovery when no entries are found."""
    import importlib.metadata
    from unittest.mock import MagicMock

    from dotevals.executors.registry import executor_registry

    # Mock entry_points() to return empty
    mock_entry_points = MagicMock()

    if hasattr(importlib.metadata.entry_points(), "select"):
        mock_entry_points.select.return_value = []
    else:
        mock_entry_points.get.return_value = None

    monkeypatch.setattr(importlib.metadata, "entry_points", lambda: mock_entry_points)

    # Force discovery - should not raise an error
    executor_registry._discovered = False
    executor_registry.discover_plugins()

    # Should still have the built-in executors
    assert executor_registry.get("foreach") is not None
    assert executor_registry.get("batch") is not None


def test_executor_registry_importlib_failure(monkeypatch):
    """Test that registry handles importlib.metadata not being available."""
    import sys

    from dotevals.executors.registry import executor_registry

    # Mock importlib.metadata to not exist
    old_metadata = sys.modules.get("importlib.metadata")
    sys.modules["importlib.metadata"] = None

    try:
        # Force discovery - should not raise an error
        executor_registry._discovered = False
        executor_registry.discover_plugins()

        # Should still have the built-in executors
        assert executor_registry.get("foreach") is not None
        assert executor_registry.get("batch") is not None
    finally:
        # Restore importlib.metadata
        if old_metadata is not None:
            sys.modules["importlib.metadata"] = old_metadata
        else:
            sys.modules.pop("importlib.metadata", None)
