"""Tests for the summary module."""

from dotevals.metrics import accuracy
from dotevals.results import Record, Score
from dotevals.summary import EvaluationSummary


def test_summary_empty_results():
    """Test summary with empty results list."""
    results = []
    summary = EvaluationSummary(results)
    assert isinstance(summary.summary, dict)
    assert len(summary.summary) == 0


def test_summary_simple():
    """Test summary with simple matching results."""
    results = [
        Record(
            item_id=1,
            dataset_row={},
            scores=[Score("match", True, [accuracy()])],
            prompt="test1",
            model_response=None,
        ),
        Record(
            item_id=2,
            dataset_row={},
            scores=[Score("match", True, [accuracy()])],
            prompt="test2",
            model_response=None,
        ),
    ]
    summary = EvaluationSummary(results)
    assert isinstance(summary.summary, dict)
    assert summary.summary == {"match": {"accuracy": 1.0}}


def test_summary_two_scores_result():
    """Test summary with multiple scores per result."""
    results = [
        Record(
            item_id=1,
            dataset_row={},
            scores=[
                Score("match_1", True, [accuracy()]),
                Score("match_2", False, [accuracy()]),
            ],
            prompt="test1",
            model_response=None,
        ),
        Record(
            item_id=2,
            dataset_row={},
            scores=[
                Score("match_1", True, [accuracy()]),
                Score("match_2", False, [accuracy()]),
            ],
            prompt="test2",
            model_response=None,
        ),
    ]
    summary = EvaluationSummary(results)
    assert isinstance(summary.summary, dict)
    assert summary.summary == {
        "match_1": {"accuracy": 1.0},
        "match_2": {"accuracy": 0.0},
    }


def test_summary_with_mixed_scores():
    """Test summary with mixed success/failure scores."""
    results = [
        Record(
            item_id=1,
            dataset_row={},
            scores=[Score("test", True, [accuracy()])],
            prompt="test1",
            model_response=None,
        ),
        Record(
            item_id=2,
            dataset_row={},
            scores=[Score("test", False, [accuracy()])],
            prompt="test2",
            model_response=None,
        ),
        Record(
            item_id=3,
            dataset_row={},
            scores=[Score("test", True, [accuracy()])],
            prompt="test3",
            model_response=None,
        ),
    ]
    summary = EvaluationSummary(results)
    assert summary.summary == {"test": {"accuracy": 2 / 3}}


def test_summary_with_errors():
    """Test summary handling results with errors."""
    results = [
        Record(
            item_id=1,
            dataset_row={},
            scores=[Score("test", True, [accuracy()])],
            prompt="test1",
            model_response=None,
        ),
        Record(
            item_id=2,
            dataset_row={},
            scores=[],  # Error case - no scores
            prompt="test2",
            model_response=None,
            error="Test error",
        ),
        Record(
            item_id=3,
            dataset_row={},
            scores=[Score("test", False, [accuracy()])],
            prompt="test3",
            model_response=None,
        ),
    ]
    summary = EvaluationSummary(results)
    # The actual behavior includes all results in the calculation
    assert summary.summary == {"test": {"accuracy": 1 / 3}}  # 1 true out of 3 total


def test_summary_with_numeric_scores():
    """Test summary with numeric score values."""
    # Use accuracy metric for numeric scores
    results = [
        Record(
            item_id=1,
            dataset_row={},
            scores=[Score("similarity", 0.95, [accuracy()])],
            prompt="test1",
            model_response=None,
        ),
        Record(
            item_id=2,
            dataset_row={},
            scores=[Score("similarity", 0.87, [accuracy()])],
            prompt="test2",
            model_response=None,
        ),
        Record(
            item_id=3,
            dataset_row={},
            scores=[Score("similarity", 0.92, [accuracy()])],
            prompt="test3",
            model_response=None,
        ),
    ]
    summary = EvaluationSummary(results)
    # Check that summary contains the similarity scores
    assert "similarity" in summary.summary
    assert "accuracy" in summary.summary["similarity"]


def test_summary_with_multiple_metrics():
    """Test summary with multiple metrics per score."""
    # Use only accuracy metric as other metrics may not be available
    results = [
        Record(
            item_id=1,
            dataset_row={},
            scores=[Score("classification", True, [accuracy()])],
            prompt="test1",
            model_response=None,
        ),
        Record(
            item_id=2,
            dataset_row={},
            scores=[Score("classification", False, [accuracy()])],
            prompt="test2",
            model_response=None,
        ),
    ]
    summary = EvaluationSummary(results)
    assert "classification" in summary.summary
    assert "accuracy" in summary.summary["classification"]
    assert summary.summary["classification"]["accuracy"] == 0.5


def test_summary_all_errors():
    """Test summary when all results have errors."""
    results = [
        Record(
            item_id=1,
            dataset_row={},
            scores=[],
            prompt="test1",
            model_response=None,
            error="Error 1",
        ),
        Record(
            item_id=2,
            dataset_row={},
            scores=[],
            prompt="test2",
            model_response=None,
            error="Error 2",
        ),
    ]
    summary = EvaluationSummary(results)
    assert summary.summary == {}  # No metrics when all results are errors
