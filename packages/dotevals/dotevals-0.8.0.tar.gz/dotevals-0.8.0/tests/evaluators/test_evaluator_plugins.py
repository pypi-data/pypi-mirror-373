"""Tests for the evaluator and metric plugin system."""

from unittest.mock import Mock, patch

import pytest

from dotevals.evaluators import evaluator
from dotevals.evaluators.registry import registry as evaluator_registry
from dotevals.metrics import Metric, metric
from dotevals.metrics.registry import registry as metric_registry


class TestEvaluatorRegistry:
    """Test the evaluator registry functionality."""

    def test_builtin_evaluators_registered(self):
        """Test that built-in evaluators are registered."""
        # Built-in evaluators should be available
        assert "exact_match" in evaluator_registry.list_evaluators()
        assert "numeric_match" in evaluator_registry.list_evaluators()
        assert "valid_json" in evaluator_registry.list_evaluators()

    def test_get_evaluator(self):
        """Test retrieving an evaluator from the registry."""
        exact_match = evaluator_registry.get("exact_match")
        assert exact_match is not None
        assert callable(exact_match)

    def test_register_custom_evaluator(self):
        """Test registering a custom evaluator."""

        @evaluator(metrics=[])
        def custom_eval(result, expected):
            return result == expected

        evaluator_registry.register("custom_eval", custom_eval)

        assert "custom_eval" in evaluator_registry.list_evaluators()
        retrieved = evaluator_registry.get("custom_eval")
        assert retrieved is custom_eval

    def test_get_nonexistent_evaluator(self):
        """Test getting a non-existent evaluator returns None."""
        assert evaluator_registry.get("nonexistent") is None

    @patch("importlib.metadata.entry_points")
    def test_load_plugins(self, mock_entry_points):
        """Test loading evaluator plugins from entry points."""
        # Mock an evaluator function
        mock_evaluator = Mock()

        # Mock entry point
        mock_entry_point = Mock()
        mock_entry_point.name = "plugin_evaluator"
        mock_entry_point.load.return_value = mock_evaluator

        # Mock entry_points return value for Python 3.10+
        mock_eps = Mock()
        mock_eps.select.return_value = [mock_entry_point]
        mock_entry_points.return_value = mock_eps

        # Force reload of plugins
        evaluator_registry._plugins_loaded = False
        evaluator_registry.load_plugins()

        # Check that the plugin was loaded
        assert evaluator_registry.get("plugin_evaluator") is mock_evaluator

    @patch("importlib.metadata.entry_points")
    def test_plugin_load_error_handling(self, mock_entry_points):
        """Test that plugin loading errors are handled gracefully."""
        # Mock entry point that fails to load
        mock_entry_point = Mock()
        mock_entry_point.name = "bad_plugin"
        mock_entry_point.load.side_effect = ImportError("Module not found")

        # Mock entry_points return value
        mock_eps = Mock()
        mock_eps.select.return_value = [mock_entry_point]
        mock_entry_points.return_value = mock_eps

        # This should not raise an exception
        evaluator_registry._plugins_loaded = False
        with pytest.warns(UserWarning, match="Failed to load evaluator plugin"):
            evaluator_registry.load_plugins()


class TestMetricRegistry:
    """Test the metric registry functionality."""

    def test_builtin_metrics_registered(self):
        """Test that built-in metrics are registered."""
        assert "accuracy" in metric_registry.list_metrics()

    def test_get_metric(self):
        """Test retrieving a metric from the registry."""
        accuracy = metric_registry.get("accuracy")
        assert accuracy is not None
        assert callable(accuracy)

    def test_register_custom_metric(self):
        """Test registering a custom metric."""

        @metric
        def custom_metric() -> Metric:
            def metric_fn(scores: list[bool]) -> float:
                return sum(scores) / len(scores) if scores else 0.0

            return metric_fn

        metric_registry.register("custom_metric", custom_metric)

        assert "custom_metric" in metric_registry.list_metrics()
        retrieved = metric_registry.get("custom_metric")
        assert retrieved is custom_metric

    @patch("importlib.metadata.entry_points")
    def test_load_metric_plugins(self, mock_entry_points):
        """Test loading metric plugins from entry points."""
        # Mock a metric function
        mock_metric = Mock()

        # Mock entry point
        mock_entry_point = Mock()
        mock_entry_point.name = "plugin_metric"
        mock_entry_point.load.return_value = mock_metric

        # Mock entry_points return value for Python 3.10+
        mock_eps = Mock()
        mock_eps.select.return_value = [mock_entry_point]
        mock_entry_points.return_value = mock_eps

        # Force reload of plugins
        metric_registry._plugins_loaded = False
        metric_registry.load_plugins()

        # Check that the plugin was loaded
        assert metric_registry.get("plugin_metric") is mock_metric


class TestDynamicImports:
    """Test dynamic import functionality."""

    def test_import_builtin_evaluator(self):
        """Test importing a built-in evaluator."""
        from dotevals.evaluators import exact_match

        assert callable(exact_match)

    def test_import_builtin_metric(self):
        """Test importing a built-in metric."""
        from dotevals.metrics import accuracy

        assert callable(accuracy)

    def test_import_nonexistent_evaluator(self):
        """Test importing a non-existent evaluator raises AttributeError."""
        import dotevals.evaluators

        with pytest.raises(AttributeError, match="No evaluator named 'nonexistent'"):
            dotevals.evaluators.nonexistent

    def test_import_nonexistent_metric(self):
        """Test importing a non-existent metric raises AttributeError."""
        import dotevals.metrics

        with pytest.raises(AttributeError, match="No metric named 'nonexistent'"):
            dotevals.metrics.nonexistent

    def test_dir_evaluators(self):
        """Test __dir__ includes all evaluators."""
        import dotevals.evaluators

        dir_contents = dir(dotevals.evaluators)

        # Should include module exports
        assert "evaluator" in dir_contents
        assert "registry" in dir_contents

        # Should include registered evaluators
        assert "exact_match" in dir_contents
        assert "numeric_match" in dir_contents

    def test_dir_metrics(self):
        """Test __dir__ includes all metrics."""
        import dotevals.metrics

        dir_contents = dir(dotevals.metrics)

        # Should include module exports
        assert "Metric" in dir_contents
        assert "metric" in dir_contents
        assert "registry" in dir_contents

        # Should include registered metrics
        assert "accuracy" in dir_contents


class TestBackwardCompatibility:
    """Test backward compatibility features."""

    def test_legacy_metric_registry(self):
        """Test that the legacy registry dict is still accessible."""
        from dotevals.metrics import registry

        # Should be the dict from base.py
        assert isinstance(registry, dict)
        assert "accuracy" in registry

        # Should be able to add custom metrics
        def custom_metric(scores):
            return sum(scores) / len(scores)

        registry["custom"] = custom_metric
        assert registry["custom"] is custom_metric
