"""Tests for dotevals exceptions."""

from dotevals.exceptions import (
    ConfigurationError,
    DatasetNotFoundError,
    EvaluationError,
    EvaluationNotFoundError,
    ExperimentExistsError,
    ExperimentNotFoundError,
    InvalidResultError,
    PluginLoadError,
    PluginNotFoundError,
)


def test_storage_exceptions():
    """Test storage-related exceptions."""
    e1 = ExperimentNotFoundError("exp1")
    assert e1.experiment_name == "exp1"
    assert "exp1" in str(e1)

    e2 = ExperimentExistsError("exp2")
    assert e2.experiment_name == "exp2"
    assert "already exists" in str(e2)

    e3 = EvaluationNotFoundError("exp", "eval")
    assert e3.experiment_name == "exp"
    assert e3.evaluation_name == "eval"
    assert "eval" in str(e3) and "exp" in str(e3)


def test_plugin_exceptions():
    """Test plugin-related exceptions."""
    e1 = PluginNotFoundError("storage", "s3")
    assert e1.plugin_type == "storage"
    assert e1.plugin_name == "s3"
    assert "storage plugin 's3'" in str(e1)

    original = ImportError("failed")
    e2 = PluginLoadError("plugin", original)
    assert e2.original_error == original
    assert "Failed to load" in str(e2)


def test_other_exceptions():
    """Test other exception types."""
    e1 = DatasetNotFoundError("mnist")
    assert e1.dataset_name == "mnist"
    assert "mnist" in str(e1)

    e2 = InvalidResultError("evaluator", dict)
    assert e2.result_type is dict
    assert "dict" in str(e2)
    assert "Result objects" in str(e2)

    # Base exceptions
    assert str(EvaluationError("failed")) == "failed"
    assert str(ConfigurationError("bad")) == "bad"
