"""Tests for BatchExecutor implementation."""

import asyncio
from unittest.mock import MagicMock

import pytest

from dotevals.evaluators import exact_match
from dotevals.executors.batch import BatchExecutor
from dotevals.results import Result, Score
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


@pytest.fixture
def simple_dataset():
    """Basic 3-item dataset for testing."""
    return [("a", 1), ("b", 2), ("c", 3)]


@pytest.fixture
def large_dataset():
    """100-item dataset for sampling tests."""
    return [(str(i), i) for i in range(100)]


@pytest.fixture
def session_manager(tmp_path):
    """Session manager with JSON storage."""
    import uuid

    unique_id = str(uuid.uuid4())[:8]
    return SessionManager(
        evaluation_name=f"test_batch_{unique_id}",
        experiment_name=f"test_exp_{unique_id}",
        storage=f"json://{tmp_path}/evaluations",
    )


class TestBatchExecutor:
    """Tests for BatchExecutor class."""

    @pytest.mark.asyncio
    async def test_executor_direct_call(self, simple_dataset, session_manager):
        """Test calling BatchExecutor directly."""

        def eval_batch_fn(text, number):
            results = []
            for t, n in zip(text, number):
                results.append(Result(exact_match(t, t)))
            return results

        executor = BatchExecutor()
        mock_eval = create_mock_evaluation(eval_batch_fn, simple_dataset, "text,number")
        summary = await executor.execute(
            mock_eval,
            session_manager,
            samples=None,
        )

        assert len(summary.results) == 3
        assert summary.summary["exact_match"]["accuracy"] == 1.0

    @pytest.mark.asyncio
    async def test_executor_with_batch_size(self, session_manager):
        """Test BatchExecutor with specific batch size."""
        dataset = [(str(i), i) for i in range(10)]
        call_count = 0
        batch_sizes = []

        def eval_batch_fn(text, number):
            nonlocal call_count, batch_sizes
            call_count += 1
            batch_sizes.append(len(text))

            results = []
            for t, n in zip(text, number):
                results.append(Result(exact_match(int(t), n)))
            return results

        executor = BatchExecutor()
        mock_eval = create_mock_evaluation(eval_batch_fn, dataset, "text,number")
        summary = await executor.execute(
            mock_eval,
            session_manager,
            batch_size=3,
        )

        # Should be called 4 times with batch sizes: 3, 3, 3, 1
        assert call_count == 4
        assert batch_sizes == [3, 3, 3, 1]
        assert len(summary.results) == 10
        assert summary.summary["exact_match"]["accuracy"] == 1.0

    @pytest.mark.asyncio
    async def test_executor_no_batch_size(self, session_manager):
        """Test BatchExecutor without batch size processes all items in one batch."""
        dataset = [(str(i), i) for i in range(5)]
        call_count = 0
        batch_sizes = []

        def eval_batch_fn(text, number):
            nonlocal call_count, batch_sizes
            call_count += 1
            batch_sizes.append(len(text))

            results = []
            for t, n in zip(text, number):
                results.append(Result(exact_match(int(t), n)))
            return results

        executor = BatchExecutor()  # No batch_size
        mock_eval = create_mock_evaluation(eval_batch_fn, dataset, "text,number")
        summary = await executor.execute(
            mock_eval,
            session_manager,
        )

        # Should be called 1 time with all 5 items
        assert call_count == 1
        assert batch_sizes == [5]
        assert len(summary.results) == 5

    @pytest.mark.asyncio
    async def test_executor_single_result(self, simple_dataset, session_manager):
        """Test BatchExecutor when function returns single result for entire batch."""

        def eval_batch_fn(text, number):
            # Return a single result for the entire batch
            return Result(exact_match(True, True))

        executor = BatchExecutor()
        mock_eval = create_mock_evaluation(eval_batch_fn, simple_dataset, "text,number")
        summary = await executor.execute(
            mock_eval,
            session_manager,
        )

        # Should create 3 records (one for each item) with the same result
        assert len(summary.results) == 3
        assert all(r.scores[0].value for r in summary.results)
        assert summary.summary["exact_match"]["accuracy"] == 1.0

    @pytest.mark.asyncio
    async def test_executor_with_samples(self, large_dataset, session_manager):
        """Test BatchExecutor with samples parameter."""

        def eval_batch_fn(text, number):
            results = []
            for t, n in zip(text, number):
                results.append(Result(exact_match(int(t), n)))
            return results

        executor = BatchExecutor()
        mock_eval = create_mock_evaluation(eval_batch_fn, large_dataset, "text,number")
        summary = await executor.execute(
            mock_eval,
            session_manager,
            samples=25,
            batch_size=10,
        )

        assert len(summary.results) == 25

    @pytest.mark.asyncio
    async def test_executor_error_handling(self, simple_dataset, session_manager):
        """Test BatchExecutor error handling."""

        def eval_batch_fn(text, number):
            raise ValueError("Test batch error")

        executor = BatchExecutor()
        mock_eval = create_mock_evaluation(eval_batch_fn, simple_dataset, "text,number")
        summary = await executor.execute(
            mock_eval,
            session_manager,
        )

        # Check we have 3 error results (one for each item in the batch)
        assert len(summary.results) == 3
        error_results = [r for r in summary.results if r.error]
        assert len(error_results) == 3
        assert all("ValueError: Test batch error" in r.error for r in error_results)

    @pytest.mark.asyncio
    async def test_executor_async_evaluation(self, simple_dataset, session_manager):
        """Test BatchExecutor with async evaluation function."""

        async def eval_batch_fn(text, number):
            await asyncio.sleep(0.001)  # Simulate async work
            results = []
            for t, n in zip(text, number):
                results.append(Result(exact_match(t, t)))
            return results

        executor = BatchExecutor()
        mock_eval = create_mock_evaluation(eval_batch_fn, simple_dataset, "text,number")
        summary = await executor.execute(
            mock_eval,
            session_manager,
        )

        assert summary.summary["exact_match"]["accuracy"] == 1.0
        assert len(summary.results) == 3


class TestBatchExecutorErrorHandling:
    """Test error handling edge cases in batch executor."""

    def test_batch_with_error_in_evaluation(self, tmp_path):
        """Test batch processing when evaluation function raises error."""
        executor = BatchExecutor()

        def eval_batch_with_error(value):
            # Simulate error during batch processing
            if 0 in value:
                raise ValueError("Cannot process zero")
            return [Result(exact_match(v, v)) for v in value]

        dataset = [(0,), (1,), (2,)]

        session_manager = SessionManager(
            experiment_name="test_errors",
            evaluation_name="test_eval",
            storage=f"json://{tmp_path}/evaluations",
        )

        # This should handle the error gracefully
        mock_eval = create_mock_evaluation(eval_batch_with_error, dataset, "value")
        summary = asyncio.run(
            executor.execute(
                mock_eval,
                session_manager,
                batch_size=3,
            )
        )

        # Should have error records
        assert summary is not None
        assert len(summary.results) == 3
        # All should have errors since the batch failed
        assert all(r.error is not None for r in summary.results)

    def test_batch_empty_dataset(self, tmp_path):
        """Test batch executor with empty dataset."""
        executor = BatchExecutor()

        def eval_batch(value):
            return [Result(exact_match(v, v)) for v in value]

        session_manager = SessionManager(
            experiment_name="test_empty",
            evaluation_name="test_eval",
            storage=f"json://{tmp_path}/evaluations",
        )

        mock_eval = create_mock_evaluation(eval_batch, [], "value")
        summary = asyncio.run(
            executor.execute(
                mock_eval,
                session_manager,
                batch_size=10,
            )
        )

        assert summary is not None
        assert len(summary.results) == 0

    def test_batch_with_different_batch_sizes(self, tmp_path):
        """Test batch executor with different batch sizes."""
        executor = BatchExecutor()

        call_count = 0
        batch_sizes_seen = []

        def eval_batch(value):
            nonlocal call_count, batch_sizes_seen
            call_count += 1
            batch_sizes_seen.append(len(value))
            return [Result(exact_match(v, v)) for v in value]

        dataset = [(i,) for i in range(10)]

        session_manager = SessionManager(
            experiment_name="test_batch_size",
            evaluation_name="test_eval",
            storage=f"json://{tmp_path}/evaluations",
        )

        # Test with batch size 3
        mock_eval = create_mock_evaluation(eval_batch, dataset, "value")
        summary = asyncio.run(
            executor.execute(
                mock_eval,
                session_manager,
                batch_size=3,
            )
        )

        assert summary is not None
        assert len(summary.results) == 10
        # Should have been called 4 times: 3, 3, 3, 1
        assert call_count == 4
        assert batch_sizes_seen == [3, 3, 3, 1]

    @pytest.mark.asyncio
    async def test_executor_kwargs_handling(self, simple_dataset, session_manager):
        """Test that executor correctly handles additional kwargs."""

        def eval_batch_fn(text, number, custom_param=None, another_param=42):
            assert custom_param == "test_value"
            assert another_param == 100
            results = []
            for t, n in zip(text, number):
                results.append(Result(exact_match(t, t)))
            return results

        executor = BatchExecutor()
        mock_eval = create_mock_evaluation(eval_batch_fn, simple_dataset, "text,number")
        summary = await executor.execute(
            mock_eval,
            session_manager,
            custom_param="test_value",
            another_param=100,
        )

        assert summary.summary["exact_match"]["accuracy"] == 1.0
        assert len(summary.results) == 3

    @pytest.mark.asyncio
    async def test_executor_empty_dataset(self, session_manager):
        """Test BatchExecutor with empty dataset."""

        def eval_batch_fn(text):
            return []

        executor = BatchExecutor()
        mock_eval = create_mock_evaluation(eval_batch_fn, [], "text")
        summary = await executor.execute(mock_eval, session_manager)

        assert summary.summary == {}
        assert len(summary.results) == 0

    @pytest.mark.asyncio
    async def test_executor_batch_size_from_kwargs(self, session_manager):
        """Test BatchExecutor picks up batch_size from kwargs."""
        dataset = [(str(i), i) for i in range(7)]
        call_count = 0
        batch_sizes = []

        def eval_batch_fn(text, number):
            nonlocal call_count, batch_sizes
            call_count += 1
            batch_sizes.append(len(text))

            results = []
            for t, n in zip(text, number):
                results.append(Result(exact_match(int(t), n)))
            return results

        executor = BatchExecutor()  # No batch_size in constructor
        mock_eval = create_mock_evaluation(eval_batch_fn, dataset, "text,number")
        summary = await executor.execute(
            mock_eval,
            session_manager,
            batch_size=4,  # Pass batch_size via kwargs
        )

        # Should be called 2 times with batch sizes: 4, 3
        assert call_count == 2
        assert batch_sizes == [4, 3]
        assert len(summary.results) == 7


# Additional error handling tests
class TestBatchExecutorAdvancedErrorHandling:
    """Test advanced error handling paths in BatchExecutor."""

    @pytest.mark.asyncio
    async def test_async_batch_error_handling(self, tmp_path):
        """Test error handling in async batch execution."""
        executor = BatchExecutor()

        # Create an evaluation function that fails for certain inputs
        async def failing_eval_fn(values):
            # Fail for specific values
            if 2 in values:
                raise ValueError("Cannot process value 2")
            return [Result(Score("test", v > 0, [])) for v in values]

        # Create mock session manager and progress manager
        session_manager = SessionManager(
            experiment_name="test_exp",
            evaluation_name="test_eval",
            storage=f"json://{tmp_path}",
        )

        # Create dataset
        dataset = [(0,), (1,), (2,), (3,)]  # Value 2 will cause error

        # Create evaluation mock
        evaluation = MagicMock()
        evaluation.eval_fn = failing_eval_fn
        evaluation.column_names = ["values"]
        evaluation.dataset = dataset
        evaluation.resolved_fixtures = {}

        # Execute with batch size 4 (all in one batch)
        summary = await executor.execute(
            evaluation=evaluation,
            session_manager=session_manager,
            samples=None,
            batch_size=4,
        )

        # All items should have errors since the batch failed
        assert len(summary.results) == 4
        assert all(r.error is not None for r in summary.results)
        assert "Cannot process value 2" in summary.results[0].error

    @pytest.mark.asyncio
    async def test_async_batch_partial_error_handling(self, tmp_path):
        """Test handling of errors for individual items in batch."""
        executor = BatchExecutor()

        # Create an evaluation function that processes batches
        async def batch_eval_fn(values):
            return [Result(Score("test", v > 0, [])) for v in values]

        # Mock session manager
        session_manager = SessionManager(
            experiment_name="test_exp",
            evaluation_name="test_eval",
            storage=f"json://{tmp_path}",
        )

        # Create dataset with some items that will cause errors during row conversion
        dataset = [
            (1,),
            (2,),
            (3,),
            (4,),
        ]

        evaluation = MagicMock()
        evaluation.eval_fn = batch_eval_fn
        evaluation.column_names = ["values"]
        evaluation.dataset = dataset
        evaluation.resolved_fixtures = {}

        # Execute with smaller batch size
        summary = await executor.execute(
            evaluation=evaluation,
            session_manager=session_manager,
            samples=None,
            batch_size=2,
        )

        # Should process all items
        assert len(summary.results) == 4
        assert all(r.error is None for r in summary.results)

    @pytest.mark.asyncio
    async def test_batch_size_validation(self, tmp_path):
        """Test batch size validation (line 39)."""
        executor = BatchExecutor()

        async def eval_fn(values):
            return [Result(Score("test", True, [])) for _ in values]

        session_manager = SessionManager(
            experiment_name="test_exp",
            evaluation_name="test_eval",
            storage=f"json://{tmp_path}",
        )

        dataset = [(1,), (2,), (3,)]

        evaluation = MagicMock()
        evaluation.eval_fn = eval_fn
        evaluation.column_names = ["values"]
        evaluation.dataset = dataset
        evaluation.resolved_fixtures = {}

        # Test with batch_size=None (should use default)
        summary = await executor.execute(
            evaluation=evaluation,
            session_manager=session_manager,
            samples=None,
            batch_size=None,  # Will use default
        )

        assert len(summary.results) == 3

    @pytest.mark.asyncio
    async def test_batch_result_length_mismatch(self, tmp_path):
        """Test error when batch function returns wrong number of results (line 179)."""
        executor = BatchExecutor()

        # Function that returns wrong number of results
        async def mismatched_eval_fn(values):
            # Return fewer results than items
            return [Result(Score("test", True, []))]  # Only 1 result for multiple items

        session_manager = SessionManager(
            experiment_name="test_exp",
            evaluation_name="test_eval",
            storage=f"json://{tmp_path}",
        )

        dataset = [(1,), (2,), (3,)]

        evaluation = MagicMock()
        evaluation.eval_fn = mismatched_eval_fn
        evaluation.column_names = ["values"]
        evaluation.dataset = dataset
        evaluation.resolved_fixtures = {}

        # Should handle the mismatch error
        summary = await executor.execute(
            evaluation=evaluation,
            session_manager=session_manager,
            samples=None,
            batch_size=3,  # All in one batch
        )

        # All items should have errors
        assert len(summary.results) == 3
        assert all(r.error is not None for r in summary.results)
        assert "returned 1 results but batch has 3 items" in summary.results[0].error

    @pytest.mark.asyncio
    async def test_batch_single_result_replication(self, tmp_path):
        """Test handling of single result for entire batch."""
        executor = BatchExecutor()

        # Function that returns single result for batch
        async def single_result_fn(values):
            # Return single result object (not a list)
            return Result(Score("batch_score", sum(values) > 0, []))

        session_manager = SessionManager(
            experiment_name="test_exp",
            evaluation_name="test_eval",
            storage=f"json://{tmp_path}",
        )

        dataset = [(1,), (2,), (3,)]

        evaluation = MagicMock()
        evaluation.eval_fn = single_result_fn
        evaluation.column_names = ["values"]
        evaluation.dataset = dataset
        evaluation.resolved_fixtures = {}

        summary = await executor.execute(
            evaluation=evaluation,
            session_manager=session_manager,
            samples=None,
            batch_size=3,
        )

        # Should replicate result for each item
        assert len(summary.results) == 3
        assert all(r.scores[0].name == "batch_score" for r in summary.results)
        assert all(r.scores[0].value is True for r in summary.results)

    def test_sync_batch_execution_fallback(self, tmp_path):
        """Test sync execution for non-async eval functions."""
        executor = BatchExecutor()

        # Sync evaluation function
        def sync_eval_fn(values):
            return [Result(Score("test", v > 0, [])) for v in values]

        session_manager = SessionManager(
            experiment_name="test_exp",
            evaluation_name="test_eval",
            storage=f"json://{tmp_path}",
        )

        dataset = [(1,), (0,), (2,)]

        evaluation = MagicMock()
        evaluation.eval_fn = sync_eval_fn
        evaluation.column_names = ["values"]
        evaluation.dataset = dataset
        evaluation.resolved_fixtures = {}

        # Run sync execution (will be wrapped in async)
        summary = asyncio.run(
            executor.execute(
                evaluation=evaluation,
                session_manager=session_manager,
                samples=None,
                batch_size=2,
            )
        )

        assert len(summary.results) == 3
        assert summary.results[0].scores[0].value is True
        assert summary.results[1].scores[0].value is False
        assert summary.results[2].scores[0].value is True

    @pytest.mark.asyncio
    async def test_empty_batch_handling(self, tmp_path):
        """Test handling of empty batches."""
        executor = BatchExecutor()

        # Mock an eval function
        async def eval_fn(values):
            if not values:
                raise ValueError("Empty batch")
            return [Result(Score("test", True, [])) for _ in values]

        session_manager = SessionManager(
            experiment_name="test_exp",
            evaluation_name="test_eval",
            storage=f"json://{tmp_path}",
        )

        # Create evaluation mock with special dataset that might create empty batches
        evaluation = MagicMock()
        evaluation.eval_fn = eval_fn
        evaluation.column_names = ["values"]
        evaluation.dataset = []  # Empty dataset
        evaluation.resolved_fixtures = {}

        # Should handle empty dataset gracefully
        summary = await executor.execute(
            evaluation=evaluation,
            session_manager=session_manager,
            samples=None,
            batch_size=10,
        )

        assert len(summary.results) == 0
