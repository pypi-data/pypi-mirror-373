"""Tests for the results module."""

import time

from dotevals.metrics import accuracy
from dotevals.results import (
    EvaluationMetadata,
    EvaluationStatus,
    Record,
    Result,
    Score,
)


def test_score_creation():
    """Test Score dataclass creation."""
    score = Score("test_metric", 0.95, [accuracy()], {"threshold": 0.9})
    assert score.name == "test_metric"
    assert score.value == 0.95
    assert len(score.metrics) == 1
    assert score.metadata == {"threshold": 0.9}


def test_score_without_metadata():
    """Test Score creation without metadata."""
    score = Score("simple", True, [])
    assert score.name == "simple"
    assert score.value is True
    assert score.metrics == []
    assert score.metadata == {}


def test_result_creation():
    """Test Result dataclass creation."""
    result = Result(Score("test", 0.5, []))
    assert len(result.scores) == 1
    assert result.scores[0].name == "test"
    assert result.scores[0].value == 0.5
    assert result.prompt is None
    assert result.model_response is None


def test_result_with_multiple_scores():
    """Test Result with multiple scores."""
    result = Result(
        Score("accuracy", 0.8, [accuracy()]),
        Score("precision", 0.9, []),
        prompt="Test prompt",
        model_response="Test response",
    )
    assert len(result.scores) == 2
    assert result.scores[0].name == "accuracy"
    assert result.scores[1].name == "precision"
    assert result.prompt == "Test prompt"
    assert result.model_response == "Test response"


def test_result_no_error_field():
    """Test that Result no longer has error field (moved to Record)."""
    result = Result(Score("test", 0.5, []))
    assert not hasattr(result, "error")
    assert len(result.scores) == 1


def test_record_creation():
    """Test Record dataclass creation."""
    record = Record(
        item_id=0,
        dataset_row={"input": "test"},
        scores=[Score("test", 1.0, [])],
        prompt=None,
        model_response=None,
    )
    assert record.dataset_row == {"input": "test"}
    assert record.item_id == 0
    assert len(record.scores) == 1
    assert record.error is None


def test_record_with_error():
    """Test Record with error."""
    record = Record(
        item_id=1,
        dataset_row={"input": "failing"},
        scores=[],
        prompt=None,
        model_response=None,
        error="Test error message",
    )
    assert record.error == "Test error message"
    assert record.scores == []
    assert record.item_id == 1


def test_record_with_full_data():
    """Test Record with all fields populated."""
    record = Record(
        item_id=42,
        dataset_row={"question": "What is 2+2?", "answer": "4"},
        scores=[
            Score("exact_match", True, [accuracy()]),
            Score("semantic_similarity", 0.95, []),
        ],
        prompt="Calculate: 2+2",
        model_response="4",
        error=None,
    )
    assert record.item_id == 42
    assert record.dataset_row["question"] == "What is 2+2?"
    assert len(record.scores) == 2
    assert record.scores[0].value is True
    assert record.scores[1].value == 0.95
    assert record.prompt == "Calculate: 2+2"
    assert record.model_response == "4"
    assert record.error is None


def test_evaluation_metadata_creation():
    """Test EvaluationMetadata dataclass."""
    eval_meta = EvaluationMetadata(
        evaluation_name="test",
        status=EvaluationStatus.RUNNING,
        started_at=time.time(),
        metadata={"model": "gpt-4"},
    )
    assert eval_meta.evaluation_name == "test"
    assert eval_meta.status == EvaluationStatus.RUNNING
    assert eval_meta.metadata == {"model": "gpt-4"}
    assert eval_meta.completed_at is None


def test_evaluation_metadata_completed():
    """Test EvaluationMetadata with completed status."""
    start_time = time.time()
    end_time = start_time + 10
    eval_meta = EvaluationMetadata(
        evaluation_name="completed_test",
        status=EvaluationStatus.COMPLETED,
        started_at=start_time,
        completed_at=end_time,
        metadata={"duration": 10},
    )
    assert eval_meta.status == EvaluationStatus.COMPLETED
    assert eval_meta.completed_at == end_time
    assert eval_meta.metadata["duration"] == 10


def test_evaluation_status_enum():
    """Test EvaluationStatus enum values."""
    assert EvaluationStatus.RUNNING.value == "running"
    assert EvaluationStatus.COMPLETED.value == "completed"
    assert EvaluationStatus.FAILED.value == "failed"

    # Test all enum values are accessible
    statuses = [
        EvaluationStatus.RUNNING,
        EvaluationStatus.COMPLETED,
        EvaluationStatus.FAILED,
    ]
    assert len(statuses) == 3
