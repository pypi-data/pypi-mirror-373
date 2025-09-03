"""Tests for the metrics registry, focusing on edge cases and plugin loading."""

import warnings
from unittest.mock import MagicMock, patch

from dotevals.metrics.registry import MetricRegistry


def test_metrics_registry_list_metrics_loads_plugins():
    """Test that list_metrics triggers plugin loading."""
    registry = MetricRegistry()

    # Reset the plugins_loaded flag to test loading
    registry._plugins_loaded = False

    with patch.object(registry, "load_plugins") as mock_load:
        registry.list_metrics()
        mock_load.assert_called_once()


def test_metrics_registry_load_plugins_only_once():
    """Test that plugins are only loaded once."""
    registry = MetricRegistry()

    # First, ensure plugins are not loaded
    registry._plugins_loaded = False

    # Load plugins
    registry.load_plugins()
    assert registry._plugins_loaded is True

    # Try to load again - should return early
    with patch("importlib.metadata.entry_points") as mock_ep:
        registry.load_plugins()
        # Should not call entry_points since plugins are already loaded
        mock_ep.assert_not_called()


def test_metrics_registry_plugin_loading_python39_path():
    """Test plugin loading for Python 3.9 compatibility path."""
    registry = MetricRegistry()
    registry._plugins_loaded = False

    # Mock entry_points to simulate Python 3.9 behavior (no select method)
    mock_entry_points = MagicMock()
    del mock_entry_points.select  # Remove select attribute

    # Create mock entry point
    mock_entry = MagicMock()
    mock_entry.name = "test_metric"
    mock_entry.load.return_value = lambda scores: sum(scores) / len(scores)

    # Set up the get method to return our mock entries
    mock_entry_points.get.return_value = [mock_entry]

    with patch("importlib.metadata.entry_points", return_value=mock_entry_points):
        registry.load_plugins()

        # Verify the Python 3.9 path was taken
        mock_entry_points.get.assert_called_with("dotevals.metrics")
        assert "test_metric" in registry._metrics


def test_metrics_registry_plugin_loading_no_group():
    """Test plugin loading when no metrics group exists (Python 3.9 path)."""
    registry = MetricRegistry()
    registry._plugins_loaded = False

    # Mock entry_points to simulate Python 3.9 behavior with no group
    mock_entry_points = MagicMock()
    del mock_entry_points.select  # Remove select attribute
    mock_entry_points.get.return_value = None  # No group found

    with patch("importlib.metadata.entry_points", return_value=mock_entry_points):
        registry.load_plugins()

        # Should complete without error
        assert registry._plugins_loaded is True
        mock_entry_points.get.assert_called_with("dotevals.metrics")


def test_metrics_registry_plugin_loading_error():
    """Test that plugin loading errors are handled gracefully."""
    registry = MetricRegistry()
    registry._plugins_loaded = False

    # Create mock entry point that raises an error
    mock_entry = MagicMock()
    mock_entry.name = "broken_metric"
    mock_entry.load.side_effect = ImportError("Module not found")

    mock_entry_points = MagicMock()
    mock_entry_points.select.return_value = [mock_entry]

    with patch("importlib.metadata.entry_points", return_value=mock_entry_points):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            registry.load_plugins()

            # Should have generated a warning
            assert len(w) == 1
            assert "Failed to load metric plugin 'broken_metric'" in str(w[0].message)
            assert "Module not found" in str(w[0].message)

    # Registry should still be marked as loaded
    assert registry._plugins_loaded is True
    # Broken metric should not be registered
    assert "broken_metric" not in registry._metrics


def test_metrics_registry_importlib_not_available():
    """Test handling when importlib.metadata is not available."""
    registry = MetricRegistry()
    registry._plugins_loaded = False

    # Simulate ImportError for importlib.metadata
    with patch("importlib.metadata.entry_points", side_effect=ImportError("No module")):
        # Should not raise, just silently skip plugin loading
        registry.load_plugins()

        # Should still mark plugins as loaded to avoid retrying
        assert registry._plugins_loaded is True


def test_metrics_registry_mixed_plugin_loading():
    """Test loading multiple plugins where some succeed and some fail."""
    registry = MetricRegistry()
    registry._plugins_loaded = False

    # Create mix of good and bad entry points
    good_entry = MagicMock()
    good_entry.name = "good_metric"
    good_entry.load.return_value = lambda scores: sum(scores) / len(scores)

    bad_entry = MagicMock()
    bad_entry.name = "bad_metric"
    bad_entry.load.side_effect = ValueError("Invalid metric")

    another_good = MagicMock()
    another_good.name = "another_metric"
    another_good.load.return_value = lambda scores: max(scores) if scores else 0

    mock_entry_points = MagicMock()
    mock_entry_points.select.return_value = [good_entry, bad_entry, another_good]

    with patch("importlib.metadata.entry_points", return_value=mock_entry_points):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            registry.load_plugins()

            # Should have one warning for the bad plugin
            assert len(w) == 1
            assert "bad_metric" in str(w[0].message)

    # Good plugins should be registered
    assert "good_metric" in registry._metrics
    assert "another_metric" in registry._metrics
    # Bad plugin should not be registered
    assert "bad_metric" not in registry._metrics


def test_metrics_registry_get_metric_loads_plugins():
    """Test that get_metric triggers plugin loading if needed."""
    registry = MetricRegistry()

    # Reset the plugins_loaded flag
    registry._plugins_loaded = False

    with patch.object(registry, "load_plugins") as mock_load:
        registry.get("some_metric")
        mock_load.assert_called_once()


def test_metrics_registry_attribute_error_handling():
    """Test handling of plugins that raise AttributeError during loading."""
    registry = MetricRegistry()
    registry._plugins_loaded = False

    # Create entry point that raises AttributeError
    mock_entry = MagicMock()
    mock_entry.name = "attr_error_metric"
    mock_entry.load.side_effect = AttributeError("Missing attribute")

    mock_entry_points = MagicMock()
    mock_entry_points.select.return_value = [mock_entry]

    with patch("importlib.metadata.entry_points", return_value=mock_entry_points):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            registry.load_plugins()

            # Should have generated a warning
            assert len(w) == 1
            assert "attr_error_metric" in str(w[0].message)
            assert "Missing attribute" in str(w[0].message)
