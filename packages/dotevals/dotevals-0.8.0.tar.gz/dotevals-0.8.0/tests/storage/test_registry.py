"""Tests for storage registry functionality."""

from dotevals.storage import get_storage, registry
from dotevals.storage.json import JSONStorage


def test_storage_module_imports(tmp_path):
    """Test that storage module exports are accessible."""
    # Test JSONStorage can be instantiated
    storage = JSONStorage(str(tmp_path))
    assert storage is not None

    # Test get_storage function
    storage2 = get_storage(f"json://{tmp_path}/storage2")
    assert isinstance(storage2, JSONStorage)


def test_storage_registry():
    """Test storage registry functionality."""

    # Test registering a custom storage
    class CustomStorage:
        def __init__(self, path):
            self.path = path

    registry.register("custom", CustomStorage)

    # Test that custom storage was registered
    assert "custom" in registry._backends
    assert registry._backends["custom"] == CustomStorage

    # Test getting storage backend
    storage_class = registry.get_backend("custom")
    assert storage_class == CustomStorage

    # Test listing storages
    assert "custom" in registry._backends
    assert "json" in registry._backends  # Default storage


def test_get_storage_with_json_protocol(tmp_path):
    """Test get_storage with json:// protocol."""
    storage = get_storage(f"json://{tmp_path}/test_storage")
    assert isinstance(storage, JSONStorage)
    assert storage.root_dir.name == "test_storage"


def test_get_storage_without_protocol(tmp_path):
    """Test get_storage defaults to JSON when no protocol specified."""
    # When no protocol is specified, it should default to JSON
    storage = get_storage(str(tmp_path / "default_storage"))
    assert isinstance(storage, JSONStorage)


def test_registry_backend_not_found():
    """Test getting non-existent backend raises ValueError."""
    import pytest

    with pytest.raises(ValueError, match="Unknown storage backend"):
        registry.get_backend("nonexistent_backend")


def test_registry_register_override():
    """Test that re-registering a backend overrides the previous one."""

    class Storage1:
        pass

    class Storage2:
        pass

    registry.register("test_backend", Storage1)
    assert registry._backends["test_backend"] == Storage1

    # Override with new class
    registry.register("test_backend", Storage2)
    assert registry._backends["test_backend"] == Storage2


def test_registry_load_plugins_entry_points(monkeypatch):
    """Test loading storage backends from entry points."""
    import importlib.metadata
    from unittest.mock import MagicMock, Mock

    from dotevals.storage.base import Storage

    # Create a mock storage class
    class PluginStorage(Storage):
        def __init__(self, path):
            self.path = path

        def create_experiment(self, experiment_name):
            pass

        def delete_experiment(self, experiment_name):
            pass

        def rename_experiment(self, old_name, new_name):
            pass

        def list_experiments(self):
            return []

        def create_evaluation(self, experiment_name, evaluation):
            pass

        def load_evaluation(self, experiment_name, evaluation_name):
            return None

        def update_evaluation_status(self, experiment_name, evaluation_name, status):
            pass

        def completed_items(self, experiment_name, evaluation_name):
            return []

        def list_evaluations(self, experiment_name):
            return []

        def add_results(self, experiment_name, evaluation_name, results):
            pass

        def get_results(self, experiment_name, evaluation_name):
            return []

        def remove_error_result(self, experiment_name, evaluation_name, item_id):
            pass

    # Mock entry point
    mock_entry_point = Mock()
    mock_entry_point.name = "plugin_storage"
    mock_entry_point.load.return_value = PluginStorage

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

    # Force reload plugins
    registry._plugins_loaded = False
    registry.load_plugins(force=True)

    # Check that the plugin was loaded
    assert "plugin_storage" in registry._backends
    assert registry._backends["plugin_storage"] == PluginStorage


def test_registry_load_plugins_error_handling(monkeypatch):
    """Test that plugin loading errors are handled gracefully."""
    import importlib.metadata
    import warnings
    from unittest.mock import MagicMock, Mock

    # Mock entry point that fails to load
    mock_entry_point = Mock()
    mock_entry_point.name = "broken_storage"
    mock_entry_point.load.side_effect = ImportError("Failed to load plugin")

    # Mock entry_points()
    mock_entry_points = MagicMock()

    if hasattr(importlib.metadata.entry_points(), "select"):
        mock_entry_points.select.return_value = [mock_entry_point]
    else:
        mock_entry_points.get.return_value = [mock_entry_point]

    monkeypatch.setattr(importlib.metadata, "entry_points", lambda: mock_entry_points)

    # Capture warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        # Force reload plugins
        registry._plugins_loaded = False
        registry.load_plugins(force=True)

        # Check that a warning was issued
        assert len(w) > 0
        assert "Failed to load storage plugin 'broken_storage'" in str(w[0].message)

    # Plugin should not be registered
    assert "broken_storage" not in registry._backends


def test_registry_load_plugins_python39_compatibility(monkeypatch):
    """Test plugin loading on Python 3.9 (no select method)."""
    import importlib.metadata
    from unittest.mock import MagicMock, Mock

    from dotevals.storage.base import Storage

    # Create a mock storage class
    class OldStyleStorage(Storage):
        def __init__(self, path):
            self.path = path

        def create_experiment(self, experiment_name):
            pass

        def delete_experiment(self, experiment_name):
            pass

        def rename_experiment(self, old_name, new_name):
            pass

        def list_experiments(self):
            return []

        def create_evaluation(self, experiment_name, evaluation):
            pass

        def load_evaluation(self, experiment_name, evaluation_name):
            return None

        def update_evaluation_status(self, experiment_name, evaluation_name, status):
            pass

        def completed_items(self, experiment_name, evaluation_name):
            return []

        def list_evaluations(self, experiment_name):
            return []

        def add_results(self, experiment_name, evaluation_name, results):
            pass

        def get_results(self, experiment_name, evaluation_name):
            return []

        def remove_error_result(self, experiment_name, evaluation_name, item_id):
            pass

    # Mock entry point
    mock_entry_point = Mock()
    mock_entry_point.name = "oldstyle_storage"
    mock_entry_point.load.return_value = OldStyleStorage

    # Mock entry_points() in Python 3.9 style (dict-like)
    mock_entry_points = MagicMock()
    # Remove select method to simulate Python 3.9
    if hasattr(mock_entry_points, "select"):
        delattr(mock_entry_points, "select")
    mock_entry_points.get.return_value = [mock_entry_point]

    monkeypatch.setattr(importlib.metadata, "entry_points", lambda: mock_entry_points)

    # Force reload plugins
    registry._plugins_loaded = False
    registry.load_plugins(force=True)

    # Check that the plugin was loaded
    assert "oldstyle_storage" in registry._backends
    assert registry._backends["oldstyle_storage"] == OldStyleStorage


def test_registry_load_plugins_no_entries(monkeypatch):
    """Test plugin loading when no entries are found."""
    import importlib.metadata
    from unittest.mock import MagicMock

    # Mock entry_points() to return empty
    mock_entry_points = MagicMock()

    if hasattr(importlib.metadata.entry_points(), "select"):
        mock_entry_points.select.return_value = []
    else:
        mock_entry_points.get.return_value = None

    monkeypatch.setattr(importlib.metadata, "entry_points", lambda: mock_entry_points)

    # Force reload plugins - should not raise an error
    registry._plugins_loaded = False
    registry.load_plugins(force=True)

    # Should still have the built-in backends
    assert "json" in registry._backends


def test_registry_list_backends_loads_plugins():
    """Test that list_backends triggers plugin loading."""
    # list_backends should load plugins if not already loaded
    backends = registry.list_backends()

    # Should at least have json backend
    assert "json" in backends
    assert isinstance(backends, list)


def test_registry_get_storage_loads_plugins():
    """Test that get_storage triggers plugin loading."""
    # This should work even if plugins haven't been loaded yet
    storage = registry.get_storage("json://.test")
    assert isinstance(storage, JSONStorage)
