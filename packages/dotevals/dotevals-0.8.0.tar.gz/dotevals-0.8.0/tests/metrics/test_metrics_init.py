"""Tests for metrics __init__ module."""

from unittest.mock import MagicMock, patch

import pytest


def test_metrics_dynamic_import():
    """Test dynamic metric import via __getattr__."""
    from dotevals import metrics

    # Test successful import of a known metric
    with patch.object(metrics.metric_registry, "get") as mock_get:
        mock_metric = MagicMock()
        mock_get.return_value = mock_metric

        result = metrics.__getattr__("accuracy")
        assert result == mock_metric
        mock_get.assert_called_once_with("accuracy")


def test_metrics_dynamic_import_not_found():
    """Test __getattr__ raises AttributeError for unknown metric."""
    from dotevals import metrics

    with patch.object(metrics.metric_registry, "get") as mock_get:
        mock_get.return_value = None
        with patch.object(metrics.metric_registry, "list_metrics") as mock_list:
            mock_list.return_value = ["accuracy", "f1_score"]

            with pytest.raises(AttributeError) as exc_info:
                metrics.__getattr__("unknown_metric")

            assert "No metric named 'unknown_metric'" in str(exc_info.value)
            assert "accuracy" in str(exc_info.value)
            assert "f1_score" in str(exc_info.value)


def test_metrics_dir():
    """Test __dir__ lists all metrics."""
    from dotevals import metrics

    with patch.object(metrics.metric_registry, "list_metrics") as mock_list:
        mock_list.return_value = ["accuracy", "f1_score", "precision"]

        result = metrics.__dir__()

        # Should include __all__ exports plus all metrics
        assert "Metric" in result
        assert "metric" in result
        assert "registry" in result
        assert "accuracy" in result
        assert "f1_score" in result
        assert "precision" in result
