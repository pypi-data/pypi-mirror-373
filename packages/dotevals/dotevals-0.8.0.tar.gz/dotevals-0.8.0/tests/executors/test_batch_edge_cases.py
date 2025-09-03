"""Tests for BatchExecutor edge cases and error handling."""

import asyncio
from unittest.mock import MagicMock

import pytest

from dotevals.evaluators import exact_match
from dotevals.executors.batch import BatchExecutor
from dotevals.results import Result
from dotevals.sessions import SessionManager


def create_mock_evaluation(eval_fn, dataset, column_spec, executor_kwargs=None):
    """Create a mock Evaluation object for testing."""
    mock_eval = MagicMock()
    mock_eval.eval_fn = eval_fn
    mock_eval.dataset = dataset
    mock_eval.column_spec = column_spec
    mock_eval.column_names = [col.strip() for col in column_spec.split(",")]
    mock_eval.executor_kwargs = executor_kwargs or {}
    return mock_eval


class TestBatchExecutorEdgeCases:
    """Test edge cases in batch executor."""

    @pytest.mark.asyncio
    async def test_batch_result_length_mismatch(self, tmp_path):
        """Test when batch function returns wrong number of results."""

        def eval_batch_wrong_length(values):
            # Return fewer results than items in batch
            return [Result(exact_match(v, v)) for v in values[:2]]

        dataset = [(1,), (2,), (3,), (4,), (5,)]

        session_manager = SessionManager(
            experiment_name="test_mismatch",
            evaluation_name="test_eval",
            storage=f"json://{tmp_path}/evaluations",
        )

        executor = BatchExecutor()
        mock_eval = create_mock_evaluation(eval_batch_wrong_length, dataset, "values")

        summary = await executor.execute(
            mock_eval,
            session_manager,
            batch_size=5,
        )

        # Should handle the error and create error records
        assert len(summary.results) == 5
        # All should have errors due to length mismatch
        error_results = [r for r in summary.results if r.error]
        assert len(error_results) == 5
        assert any(
            "returned 2 results but batch has 5 items" in r.error for r in error_results
        )

    @pytest.mark.asyncio
    async def test_batch_with_unpacking_error(self, tmp_path):
        """Test batch executor with dataset items that can't be unpacked."""

        def eval_batch(a, b):
            return [Result(exact_match(x, y)) for x, y in zip(a, b)]

        # Dataset with inconsistent tuple sizes
        dataset = [
            (1, 2),  # Good
            (3,),  # Missing second value - will cause unpacking error
            (4, 5),  # Good
        ]

        session_manager = SessionManager(
            experiment_name="test_unpacking",
            evaluation_name="test_eval",
            storage=f"json://{tmp_path}/evaluations",
        )

        executor = BatchExecutor()
        mock_eval = create_mock_evaluation(eval_batch, dataset, "a,b")

        summary = await executor.execute(
            mock_eval,
            session_manager,
            batch_size=3,
        )

        # Should have results for all items
        assert len(summary.results) == 3

        # The item with unpacking error should have an error
        error_results = [r for r in summary.results if r.error]
        assert len(error_results) >= 1
        # Check for unpacking error
        assert any(
            "unpack" in r.error.lower() or "values" in r.error.lower()
            for r in error_results
        )

    @pytest.mark.asyncio
    async def test_batch_with_partial_errors(self, tmp_path):
        """Test batch where only some items cause errors."""

        def eval_batch_partial_errors(values):
            results = []
            for v in values:
                if v == 0:
                    # Raise an error for zero values
                    raise ValueError("Division by zero in batch")
                else:
                    results.append(Result(exact_match(10 / v, 10 / v)))
            return results

        dataset = [(5,), (0,), (2,), (0,), (1,)]

        session_manager = SessionManager(
            experiment_name="test_partial",
            evaluation_name="test_eval",
            storage=f"json://{tmp_path}/evaluations",
        )

        executor = BatchExecutor()
        mock_eval = create_mock_evaluation(eval_batch_partial_errors, dataset, "values")

        summary = await executor.execute(
            mock_eval,
            session_manager,
            batch_size=5,
        )

        assert len(summary.results) == 5
        # All items should have errors since the batch fails when it encounters 0
        error_count = sum(1 for r in summary.results if r.error is not None)
        assert error_count == 5  # All items fail when batch encounters division by zero

    @pytest.mark.asyncio
    async def test_batch_with_mixed_result_types(self, tmp_path):
        """Test batch executor when evaluation returns different result types."""

        def eval_batch_mixed(values):
            results = []
            for v in values:
                if v % 2 == 0:
                    # Return empty Result for even numbers
                    results.append(Result(prompt=f"Value: {v}"))
                else:
                    # Return Result with score for odd numbers
                    results.append(Result(exact_match(v, v), prompt=f"Value: {v}"))
            return results

        dataset = [(i,) for i in range(6)]

        session_manager = SessionManager(
            experiment_name="test_mixed",
            evaluation_name="test_eval",
            storage=f"json://{tmp_path}/evaluations",
        )

        executor = BatchExecutor()
        mock_eval = create_mock_evaluation(eval_batch_mixed, dataset, "values")

        summary = await executor.execute(
            mock_eval,
            session_manager,
            batch_size=6,
        )

        assert len(summary.results) == 6
        # Check that we have results with scores (odd numbers) and without scores (even numbers)
        results_with_scores = [r for r in summary.results if r.scores]
        results_without_scores = [r for r in summary.results if not r.scores]
        assert len(results_with_scores) == 3  # Odd numbers: 1, 3, 5
        assert len(results_without_scores) == 3  # Even numbers: 0, 2, 4

    @pytest.mark.asyncio
    async def test_batch_async_with_concurrency(self, tmp_path):
        """Test async batch evaluation with simulated concurrent processing."""

        execution_order = []

        async def eval_batch_async(values):
            batch_id = values[0] if values else None
            execution_order.append(("start", batch_id))
            await asyncio.sleep(0.01)  # Simulate async work
            execution_order.append(("end", batch_id))
            return [Result(exact_match(v, v)) for v in values]

        dataset = [(i,) for i in range(10)]

        session_manager = SessionManager(
            experiment_name="test_async",
            evaluation_name="test_eval",
            storage=f"json://{tmp_path}/evaluations",
        )

        executor = BatchExecutor()
        mock_eval = create_mock_evaluation(eval_batch_async, dataset, "values")

        summary = await executor.execute(
            mock_eval,
            session_manager,
            batch_size=3,
        )

        assert len(summary.results) == 10
        # Check that batches were processed sequentially (not concurrently)
        # Each batch should complete before the next starts
        assert execution_order == [
            ("start", 0),
            ("end", 0),
            ("start", 3),
            ("end", 3),
            ("start", 6),
            ("end", 6),
            ("start", 9),
            ("end", 9),
        ]

    @pytest.mark.asyncio
    async def test_batch_with_sampling_edge_cases(self, tmp_path):
        """Test batch executor with various sampling scenarios."""

        def eval_batch(values):
            return [Result(exact_match(v, v)) for v in values]

        dataset = [(i,) for i in range(100)]

        session_manager = SessionManager(
            experiment_name="test_sampling",
            evaluation_name="test_eval",
            storage=f"json://{tmp_path}/evaluations",
        )

        executor = BatchExecutor()
        mock_eval = create_mock_evaluation(eval_batch, dataset, "values")

        # Test with samples larger than dataset
        summary = await executor.execute(
            mock_eval,
            session_manager,
            samples=200,
            batch_size=10,
        )

        # Should process entire dataset (100 items)
        assert len(summary.results) == 100

        # Test with samples equal to batch size
        session_manager2 = SessionManager(
            experiment_name="test_sampling2",
            evaluation_name="test_eval2",
            storage=f"json://{tmp_path}/evaluations",
        )

        summary2 = await executor.execute(
            mock_eval,
            session_manager2,
            samples=10,
            batch_size=10,
        )

        # Should process exactly 10 items in one batch
        assert len(summary2.results) == 10

    @pytest.mark.asyncio
    async def test_batch_with_complex_error_propagation(self, tmp_path):
        """Test error propagation through batch processing."""

        def eval_batch_complex_errors(values):
            if len(values) == 0:
                raise ValueError("Empty batch")

            results = []
            for i, v in enumerate(values):
                if i == 0 and v == 99:
                    # Special case: error on first item of last batch
                    raise RuntimeError(f"Critical error on value {v}")
                results.append(Result(exact_match(v, v)))
            return results

        dataset = [(i,) for i in range(100)]

        session_manager = SessionManager(
            experiment_name="test_complex",
            evaluation_name="test_eval",
            storage=f"json://{tmp_path}/evaluations",
        )

        executor = BatchExecutor()
        mock_eval = create_mock_evaluation(eval_batch_complex_errors, dataset, "values")

        summary = await executor.execute(
            mock_eval,
            session_manager,
            batch_size=33,  # Will create batches of 33, 33, 33, 1
        )

        assert len(summary.results) == 100
        # Last batch (item 99) should have error
        assert summary.results[99].error is not None
        assert "Critical error on value 99" in summary.results[99].error

    @pytest.mark.asyncio
    async def test_batch_with_model_response_and_prompt(self, tmp_path):
        """Test that batch executor properly handles model_response and prompt fields."""

        def eval_batch_with_fields(values):
            results = []
            for v in values:
                result = Result(
                    exact_match(v, v),
                    prompt=f"Process value: {v}",
                    model_response=f"Processed: {v * 2}",
                )
                results.append(result)
            return results

        dataset = [(i,) for i in range(5)]

        session_manager = SessionManager(
            experiment_name="test_fields",
            evaluation_name="test_eval",
            storage=f"json://{tmp_path}/evaluations",
        )

        executor = BatchExecutor()
        mock_eval = create_mock_evaluation(eval_batch_with_fields, dataset, "values")

        summary = await executor.execute(
            mock_eval,
            session_manager,
            batch_size=5,
        )

        assert len(summary.results) == 5
        for i, record in enumerate(summary.results):
            assert record.prompt == f"Process value: {i}"
            assert record.model_response == f"Processed: {i * 2}"
            assert record.error is None
