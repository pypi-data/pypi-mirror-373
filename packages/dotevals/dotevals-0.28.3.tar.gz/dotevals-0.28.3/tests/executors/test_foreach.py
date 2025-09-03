"""Tests for ForEachExecutor implementation."""

import asyncio
import time
from unittest.mock import MagicMock

import pytest

from dotevals.evaluators import exact_match
from dotevals.executors.foreach import ForEachExecutor
from dotevals.progress import BaseProgressManager
from dotevals.results import EvaluationMetadata, EvaluationStatus, Result, Score
from dotevals.sessions import SessionManager
from dotevals.storage.json import JSONStorage


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
        evaluation_name=f"test_eval_{unique_id}",
        experiment_name=f"test_exp_{unique_id}",
        storage=f"json://{tmp_path}/evaluations",
    )


class TestForEachExecutor:
    """Tests for ForEachExecutor class."""

    @pytest.mark.asyncio
    async def test_executor_direct_call(self, simple_dataset, session_manager):
        """Test calling ForEachExecutor directly."""

        def eval_fn(text, number):
            return Result(exact_match(text, text))

        executor = ForEachExecutor()
        mock_eval = create_mock_evaluation(eval_fn, simple_dataset, "text,number")
        summary = await executor.execute(mock_eval, session_manager)

        assert len(summary.results) == 3
        assert summary.summary["exact_match"]["accuracy"] == 1.0

    @pytest.mark.asyncio
    async def test_executor_with_samples(self, large_dataset, session_manager):
        """Test ForEachExecutor with samples parameter."""

        def eval_fn(text, number):
            return Result(exact_match(int(text), number))

        executor = ForEachExecutor()
        mock_eval = create_mock_evaluation(eval_fn, large_dataset, "text,number")
        summary = await executor.execute(mock_eval, session_manager, samples=5)

        assert len(summary.results) == 5

    @pytest.mark.asyncio
    async def test_executor_sequential_processing(
        self, simple_dataset, session_manager
    ):
        """Test ForEachExecutor processes items sequentially."""
        processed_order = []

        async def eval_fn(text, number):
            await asyncio.sleep(0.001)
            processed_order.append(number)
            return Result(exact_match(text, text))

        executor = ForEachExecutor()
        mock_eval = create_mock_evaluation(eval_fn, simple_dataset, "text,number")
        summary = await executor.execute(mock_eval, session_manager)

        assert len(summary.results) == 3
        assert processed_order == [1, 2, 3]  # Sequential order
        # Order may vary with concurrent execution

    @pytest.mark.asyncio
    async def test_executor_error_handling(self, simple_dataset, session_manager):
        """Test ForEachExecutor error handling."""
        call_count = 0

        def eval_fn(text, number):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise ValueError("Test error")
            return Result(exact_match(text, text))

        executor = ForEachExecutor()
        mock_eval = create_mock_evaluation(eval_fn, simple_dataset, "text,number")
        summary = await executor.execute(mock_eval, session_manager)

        # Check we have 3 total results: 2 successful and 1 error
        assert len(summary.results) == 3
        assert len([r for r in summary.results if not r.error]) == 2
        error_results = [r for r in summary.results if r.error]
        assert len(error_results) == 1
        assert "ValueError: Test error" in error_results[0].error

    @pytest.mark.asyncio
    async def test_executor_partial_failure(self, tmp_path):
        """Test handling partial failures in async evaluation."""
        import uuid

        unique_id = str(uuid.uuid4())[:8]
        session_mgr = SessionManager(
            evaluation_name=f"test_eval_{unique_id}",
            experiment_name=f"test_exp_{unique_id}",
            storage=f"json://{tmp_path}",
        )

        call_count = 0

        async def sometimes_failing(input):  # Parameter name must match column name
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise ValueError(f"Failed on item {call_count}")
            return Result(Score("test", True, []))

        dataset = [{"input": f"test_{i}"} for i in range(3)]

        executor = ForEachExecutor()
        mock_eval = create_mock_evaluation(sometimes_failing, dataset, "input")
        summary = await executor.execute(
            mock_eval,
            session_mgr,
        )

        # Check that we have 2 successful results and 1 error
        assert len(summary.results) == 3
        successful = [r for r in summary.results if not r.error]
        errors = [r for r in summary.results if r.error]

        assert len(successful) == 2
        assert len(errors) == 1

        # The second item should have failed
        assert errors[0].dataset_row == {"input": "test_1"}
        assert "ValueError" in errors[0].error
        assert "Failed on item 2" in errors[0].error

    @pytest.mark.asyncio
    async def test_executor_concurrent_errors(self, tmp_path):
        """Test error handling with concurrent async evaluation."""
        import uuid

        unique_id = str(uuid.uuid4())[:8]
        session_mgr = SessionManager(
            experiment_name=f"test_exp_{unique_id}",
            evaluation_name=f"test_eval_{unique_id}",
            storage=f"json://{tmp_path}",
        )

        async def evaluator_with_errors(id):  # Parameter name must match column name
            if id % 3 == 0:
                raise ValueError(f"Error on {id}")
            await asyncio.sleep(0.01)
            return Result(Score("test", id, []))

        dataset = [(i,) for i in range(10)]  # Use tuples for single column

        executor = ForEachExecutor()
        mock_eval = create_mock_evaluation(evaluator_with_errors, dataset, "id")
        summary = await executor.execute(
            mock_eval,
            session_mgr,
        )

        # Check that we have both successful and error results
        successful = [r for r in summary.results if not r.error]
        errors = [r for r in summary.results if r.error]

        # IDs 0, 3, 6, 9 should have errors (multiples of 3)
        assert len(errors) == 4
        assert len(successful) == 6

        # Check error messages
        for error_result in errors:
            assert "ValueError" in error_result.error
            assert "Error on" in error_result.error

    @pytest.mark.asyncio
    async def test_executor_kwargs_handling(self, simple_dataset, session_manager):
        """Test that executor correctly handles additional kwargs."""
        captured_kwargs = []

        def eval_fn(text, number, custom_param=None, another_param=42):
            captured_kwargs.append(
                {"custom_param": custom_param, "another_param": another_param}
            )
            return Result(exact_match(text, text))

        executor = ForEachExecutor()
        mock_eval = create_mock_evaluation(eval_fn, simple_dataset, "text,number")
        await executor.execute(
            mock_eval,
            session_manager,
            custom_param="test_value",
            another_param=100,
        )

        assert len(captured_kwargs) == 3
        for kwargs in captured_kwargs:
            assert kwargs["custom_param"] == "test_value"
            assert kwargs["another_param"] == 100


# Error handling tests
class MockProgressManager(BaseProgressManager):
    """Mock progress manager for testing."""

    def start_evaluation(self, dataset_name, total_items, dataset_info):
        pass

    def update_evaluation_progress(self, dataset_name, result=None):
        pass

    def complete_evaluation(self, dataset_name, summary):
        pass

    def finish(self):
        pass


class TestForEachErrorHandling:
    """Test error handling paths in ForEach executor."""

    def test_executor_name_property(self):
        """Test the name property (line 18)."""
        executor = ForEachExecutor()
        assert executor.name == "foreach"

    def test_sync_dataset_error_handling(self, tmp_path):
        """Test handling of dataset loading errors in sync execution (line 40)."""
        storage = JSONStorage(str(tmp_path))
        eval_metadata = EvaluationMetadata(
            evaluation_name="eval1",
            status=EvaluationStatus.RUNNING,
            started_at=time.time(),
        )
        storage.create_evaluation("test_exp", eval_metadata)
        session = SessionManager("eval1", "test_exp", storage)
        executor = ForEachExecutor()
        progress = MockProgressManager()

        # Create a dataset item that's an exception
        dataset_error = ValueError("Failed to load dataset item")
        dataset_items = [
            (0, {"input": "test1"}),
            (1, dataset_error),  # This is an Exception
            (2, {"input": "test3"}),
        ]

        def eval_fn(input):
            return Result(
                Score("exact_match", 1.0, []),
                prompt=input,
                model_response=f"response_{input}",
            )

        # Execute with error in dataset
        executor._execute_sync(
            eval_fn=eval_fn,
            columns=["input"],
            dataset_items=dataset_items,
            session_manager=session,
            progress_manager=progress,
            dataset_info={"name": "test_dataset"},
        )

        # Check that results were saved, including the error
        results = storage.get_results("test_exp", "eval1")
        assert len(results) == 3

        # First item should be successful
        assert results[0].error is None
        assert len(results[0].scores) == 1
        assert results[0].scores[0].name == "exact_match"
        assert results[0].scores[0].value == 1.0

        # Second item should have the dataset error
        assert results[1].error is not None
        assert "Failed to load dataset item" in str(results[1].error)

        # Third item should be successful
        assert results[2].error is None
        assert len(results[2].scores) == 1
        assert results[2].scores[0].name == "exact_match"
        assert results[2].scores[0].value == 1.0

    def test_sync_evaluation_error_handling(self, tmp_path):
        """Test handling of evaluation errors in sync execution."""
        storage = JSONStorage(str(tmp_path))
        eval_metadata = EvaluationMetadata(
            evaluation_name="eval1",
            status=EvaluationStatus.RUNNING,
            started_at=time.time(),
        )
        storage.create_evaluation("test_exp", eval_metadata)
        session = SessionManager("eval1", "test_exp", storage)
        executor = ForEachExecutor()
        progress = MockProgressManager()

        dataset_items = [
            (0, {"value": 1}),
            (1, {"value": 2}),  # This will cause an error
            (2, {"value": 3}),
        ]

        def eval_fn(value):
            if value == 2:
                raise ValueError("Cannot process value 2")
            return Result(
                Score("exact_match", 1.0, []),
                prompt=str(value),
                model_response=f"response_{value}",
            )

        # Execute with error in evaluation
        executor._execute_sync(
            eval_fn=eval_fn,
            columns=["value"],
            dataset_items=dataset_items,
            session_manager=session,
            progress_manager=progress,
            dataset_info={"name": "test_dataset"},
        )

        # Check that results were saved
        results = storage.get_results("test_exp", "eval1")
        assert len(results) == 3

        # First item should be successful
        assert results[0].error is None

        # Second item should have the evaluation error
        assert results[1].error is not None
        assert "Cannot process value 2" in str(results[1].error)

        # Third item should be successful
        assert results[2].error is None

    @pytest.mark.asyncio
    async def test_async_dataset_error_handling(self, tmp_path):
        """Test handling of dataset loading errors in async execution (line 85)."""
        storage = JSONStorage(str(tmp_path))
        eval_metadata = EvaluationMetadata(
            evaluation_name="eval1",
            status=EvaluationStatus.RUNNING,
            started_at=time.time(),
        )
        storage.create_evaluation("test_exp", eval_metadata)
        session = SessionManager("eval1", "test_exp", storage)
        executor = ForEachExecutor()
        progress = MockProgressManager()

        # Create a dataset item that's an exception
        dataset_error = RuntimeError("Async dataset loading failed")
        dataset_items = [
            (0, {"input": "test1"}),
            (1, dataset_error),  # This is an Exception
            (2, {"input": "test3"}),
        ]

        async def eval_fn(input):
            return Result(
                Score("exact_match", 1.0, []),
                prompt=input,
                model_response=f"response_{input}",
            )

        # Execute with error in dataset
        await executor._execute_async(
            eval_fn=eval_fn,
            columns=["input"],
            dataset_items=dataset_items,
            session_manager=session,
            progress_manager=progress,
            dataset_info={"name": "test_dataset"},
        )

        # Check that results were saved, including the error
        results = storage.get_results("test_exp", "eval1")
        assert len(results) == 3

        # First item should be successful
        assert results[0].error is None
        assert len(results[0].scores) == 1
        assert results[0].scores[0].name == "exact_match"
        assert results[0].scores[0].value == 1.0

        # Second item should have the dataset error
        assert results[1].error is not None
        assert "Async dataset loading failed" in str(results[1].error)

        # Third item should be successful
        assert results[2].error is None
        assert len(results[2].scores) == 1
        assert results[2].scores[0].name == "exact_match"
        assert results[2].scores[0].value == 1.0

    @pytest.mark.asyncio
    async def test_async_evaluation_error_handling(self, tmp_path):
        """Test handling of evaluation errors in async execution."""
        storage = JSONStorage(str(tmp_path))
        eval_metadata = EvaluationMetadata(
            evaluation_name="eval1",
            status=EvaluationStatus.RUNNING,
            started_at=time.time(),
        )
        storage.create_evaluation("test_exp", eval_metadata)
        session = SessionManager("eval1", "test_exp", storage)
        executor = ForEachExecutor()
        progress = MockProgressManager()

        dataset_items = [
            (0, {"value": 1}),
            (1, {"value": 2}),  # This will cause an error
            (2, {"value": 3}),
        ]

        async def eval_fn(value):
            if value == 2:
                raise RuntimeError("Async processing failed for value 2")
            return Result(
                Score("exact_match", 1.0, []),
                prompt=str(value),
                model_response=f"response_{value}",
            )

        # Execute with error in evaluation
        await executor._execute_async(
            eval_fn=eval_fn,
            columns=["value"],
            dataset_items=dataset_items,
            session_manager=session,
            progress_manager=progress,
            dataset_info={"name": "test_dataset"},
        )

        # Check that results were saved
        results = storage.get_results("test_exp", "eval1")
        assert len(results) == 3

        # First item should be successful
        assert results[0].error is None

        # Second item should have the evaluation error
        assert results[1].error is not None
        assert "Async processing failed for value 2" in str(results[1].error)

        # Third item should be successful
        assert results[2].error is None
