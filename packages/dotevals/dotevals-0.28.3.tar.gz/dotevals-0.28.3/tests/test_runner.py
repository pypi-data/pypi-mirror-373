"""Tests for the runner system."""

import asyncio
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from dotevals import foreach
from dotevals.evaluators import exact_match
from dotevals.results import Result
from dotevals.runner import Runner, _is_async_evaluation
from dotevals.sessions import SessionManager
from dotevals.summary import EvaluationSummary


# Helper to create an Evaluation with resolved fixtures for testing
def create_mock_evaluation(eval_fn, resolved_fixtures=None):
    """Create an Evaluation object for testing."""
    from dotevals.evaluation import Evaluation

    if resolved_fixtures is None:
        resolved_fixtures = {}

    # Create a real Evaluation instance with test data
    evaluation = Evaluation(
        eval_fn=eval_fn,
        dataset=[],  # Empty dataset for unit tests
        executor_name="foreach",
        column_spec="test",
        executor_kwargs={},
        resolved_fixtures=resolved_fixtures,
    )

    return evaluation


class TestRunner:
    """Tests for the Runner class."""

    @pytest.fixture
    def results_dict(self):
        """Create a results dictionary."""
        return {}

    @pytest.fixture
    def runner(self, results_dict):
        """Create a Runner instance."""
        return Runner(
            experiment_name="test_exp",
            samples=10,
            concurrent=False,
            results_dict=results_dict,
        )

    @pytest.mark.asyncio
    async def test_run_empty_evaluations(self, runner):
        """Test running with empty evaluation list."""
        await runner.run_evaluations([])
        # Should not raise

    @pytest.mark.asyncio
    async def test_run_sync_evaluation(self, runner, results_dict):
        """Test running a synchronous evaluation."""
        # Create a mock item
        mock_item = MagicMock()
        mock_item.name = "test_eval"

        # Create a sync evaluation function
        def sync_eval(session_manager, samples, progress_manager):
            # Real evaluations must return an EvaluationSummary (handled by executor)
            # For testing the runner, we'll use a mock that returns what the runner expects

            return EvaluationSummary([])

        mock_item.function = create_mock_evaluation(sync_eval)

        # Run evaluation
        await runner.run_evaluations([mock_item])

        # Check result was stored (runner stores EvaluationSummary objects)
        assert "test_eval" in results_dict
        assert isinstance(results_dict["test_eval"], EvaluationSummary)

    @pytest.mark.asyncio
    async def test_run_async_evaluation(self, runner, results_dict):
        """Test running an asynchronous evaluation."""
        # Create a mock item
        mock_item = MagicMock()
        mock_item.name = "test_async_eval"

        # Create an async evaluation function
        async def async_eval(session_manager, samples, progress_manager):
            await asyncio.sleep(0.01)  # Simulate async work

            return EvaluationSummary([])

        mock_item.function = create_mock_evaluation(async_eval)

        # Run evaluation
        await runner.run_evaluations([mock_item])

        # Check result was stored
        assert "test_async_eval" in results_dict
        assert isinstance(results_dict["test_async_eval"], EvaluationSummary)

    @pytest.mark.asyncio
    async def test_run_mixed_evaluations_sequential(self, runner, results_dict):
        """Test running mixed sync/async evaluations sequentially."""
        # Runner fixture already has concurrent=False

        # Create mock items
        sync_item = MagicMock()
        sync_item.name = "sync_eval"
        sync_item.fixtures = {}

        def sync_fn(session_manager, samples, progress_manager):
            return EvaluationSummary([])

        sync_item.function = create_mock_evaluation(sync_fn)

        async_item = MagicMock()
        async_item.name = "async_eval"
        async_item.fixtures = {}

        async def async_fn(session_manager, samples, progress_manager):
            return EvaluationSummary([])

        async_item.function = create_mock_evaluation(async_fn)

        # Mock FixtureManager

        # Run evaluations
        await runner.run_evaluations([sync_item, async_item])

        # Check both results
        assert "sync_eval" in results_dict
        assert "async_eval" in results_dict
        assert isinstance(results_dict["sync_eval"], EvaluationSummary)
        assert isinstance(results_dict["async_eval"], EvaluationSummary)

    @pytest.mark.asyncio
    async def test_run_concurrent_evaluations(self, results_dict):
        """Test running async evaluations concurrently."""
        # Create a runner with concurrent=True
        concurrent_runner = Runner(
            experiment_name="test_exp",
            samples=10,
            concurrent=True,
            results_dict=results_dict,
        )

        # Create async evaluation functions
        async def eval1(session_manager, samples, progress_manager):
            await asyncio.sleep(0.02)

            return EvaluationSummary([])

        async def eval2(session_manager, samples, progress_manager):
            await asyncio.sleep(0.01)

            return EvaluationSummary([])

        # Create async items
        item1 = MagicMock()
        item1.name = "eval1"
        item1.fixtures = {}
        item1.function = create_mock_evaluation(eval1)

        item2 = MagicMock()
        item2.name = "eval2"
        item2.fixtures = {}
        item2.function = create_mock_evaluation(eval2)

        # Spy on task creation to verify concurrency
        with patch("asyncio.create_task", wraps=asyncio.create_task) as mock_create:
            # Run evaluations
            await concurrent_runner.run_evaluations([item1, item2])

            # Verify tasks were created for concurrent execution
            assert mock_create.call_count == 2

        # Check that both evaluations completed
        assert "eval1" in results_dict
        assert "eval2" in results_dict
        assert isinstance(results_dict["eval1"], EvaluationSummary)
        assert isinstance(results_dict["eval2"], EvaluationSummary)

    @pytest.mark.asyncio
    async def test_run_real_evaluation_function(self, tmp_path):
        """Test running a real evaluation function without mocks."""
        tmpdir = tmp_path
        # Create real dataset
        test_data = [("apple", "apple"), ("banana", "banana"), ("cherry", "orange")]

        # Create real evaluation function
        @foreach("text,expected", test_data)
        def real_eval(text, expected):
            return Result(exact_match(text, expected))

        # Create real session manager
        import uuid

        unique_id = str(uuid.uuid4())[:8]
        session_manager = SessionManager(
            experiment_name=f"test_real_{unique_id}",
            evaluation_name=f"eval_real_{unique_id}",
            storage=f"json://{tmpdir}",
        )

        # Run evaluation
        summary = await real_eval(session_manager, samples=None)

        # Verify results
        assert len(summary.results) == 3
        assert summary.summary["exact_match"]["accuracy"] == 2 / 3  # 2 matches out of 3

    @pytest.mark.asyncio
    async def test_run_real_async_evaluation(self, tmp_path):
        """Test running a real async evaluation function."""
        tmpdir = tmp_path
        # Create real dataset
        test_data = [(1, 1), (2, 4), (3, 9)]

        # Create real async evaluation function
        @foreach("num,expected", test_data)
        async def real_async_eval(num, expected):
            await asyncio.sleep(0.001)  # Simulate async work
            result = num * num
            return Result(exact_match(result, expected))

        # Create real session manager
        import uuid

        unique_id = str(uuid.uuid4())[:8]
        session_manager = SessionManager(
            experiment_name=f"test_async_{unique_id}",
            evaluation_name=f"eval_async_{unique_id}",
            storage=f"json://{tmpdir}",
        )

        # Run evaluation
        summary = await real_async_eval(session_manager, samples=None)

        # Verify results
        assert len(summary.results) == 3
        assert summary.summary["exact_match"]["accuracy"] == 1.0  # All squares match

    @pytest.mark.asyncio
    async def test_run_real_evaluation_with_errors(self, tmp_path):
        """Test running a real evaluation that has some errors."""
        tmpdir = tmp_path
        # Create real dataset
        test_data = [("valid1", "ok"), ("error", "fail"), ("valid2", "ok")]

        # Create evaluation function that raises errors
        @foreach("input,expected", test_data)
        def eval_with_errors(input, expected):
            if input == "error":
                raise ValueError("Intentional error for testing")
            return Result(exact_match(expected, "ok"))

        # Create real session manager
        import uuid

        unique_id = str(uuid.uuid4())[:8]
        session_manager = SessionManager(
            experiment_name=f"test_errors_{unique_id}",
            evaluation_name=f"eval_errors_{unique_id}",
            storage=f"json://{tmpdir}",
        )

        # Run evaluation - should handle errors gracefully
        summary = await eval_with_errors(session_manager, samples=None)

        # Verify results
        assert len(summary.results) == 3
        # Check we have 2 successes and 1 error
        errors = [r for r in summary.results if r.error is not None]
        successes = [r for r in summary.results if r.error is None]
        assert len(errors) == 1
        assert len(successes) == 2
        assert "ValueError" in errors[0].error


class TestRunnerEdgeCases:
    """Edge case tests for Runner."""

    @pytest.mark.asyncio
    async def test_runner_with_fixture_kwargs_error(self):
        """Test Runner when fixture kwargs are missing."""
        results_dict = {}
        runner = Runner(results_dict=results_dict)

        # Create item without fixtures
        mock_item = MagicMock()
        mock_item.name = "test"
        del mock_item.fixtures  # Remove the attribute

        def eval_fn(session_manager, samples, progress_manager):
            return EvaluationSummary([])

        mock_item.function = create_mock_evaluation(eval_fn)

        # Should still work, using empty dict
        await runner.run_evaluations([mock_item])

        assert "test" in results_dict
        assert isinstance(results_dict["test"], EvaluationSummary)

    @pytest.mark.asyncio
    async def test_runner_progress_manager(self):
        """Test Runner progress manager functionality."""
        results = {}
        runner = Runner(results_dict=results)

        # Verify progress manager is created
        assert hasattr(runner, "progress_manager")

        # Create multiple items to test progress
        items = []
        for i in range(3):
            item = MagicMock()
            item.name = f"test_{i}"
            item.fixtures = {}

            def eval_fn(session_manager, samples, progress_manager):
                return EvaluationSummary([])

            item.function = create_mock_evaluation(eval_fn)
            items.append(item)

        # Mock FixtureManager and progress manager

        with patch.object(runner.progress_manager, "start") as mock_start:
            with patch.object(runner.progress_manager, "finish") as mock_finish:
                await runner.run_evaluations(items)

                # Verify progress tracking
                mock_start.assert_called_once_with(3)
                mock_finish.assert_called_once()


class TestRunnerConcurrentTasks:
    """Test Runner concurrent task handling."""

    @pytest.mark.asyncio
    async def test_concurrent_task_creation(self):
        """Test concurrent task creation code path."""
        results = {}
        runner = Runner(concurrent=True, results_dict=results)

        # Create async items
        async def eval1(session_manager, samples, progress_manager):
            await asyncio.sleep(0.01)

            return EvaluationSummary([])

        async def eval2(session_manager, samples, progress_manager):
            await asyncio.sleep(0.01)

            return EvaluationSummary([])

        item1 = MagicMock()
        item1.name = "eval1"
        item1.fixtures = {}
        item1.function = create_mock_evaluation(eval1)

        item2 = MagicMock()
        item2.name = "eval2"
        item2.fixtures = {}
        item2.function = create_mock_evaluation(eval2)

        # Spy on asyncio to verify task creation
        with patch("asyncio.create_task", wraps=asyncio.create_task) as mock_create:
            await runner.run_evaluations([item1, item2])

            # Verify tasks were created
            assert mock_create.call_count == 2

        # Verify results
        assert "eval1" in results
        assert "eval2" in results
        assert isinstance(results["eval1"], EvaluationSummary)
        assert isinstance(results["eval2"], EvaluationSummary)


class TestRunnerUtilities:
    """Tests for runner utility functions."""

    def test_is_async_evaluation(self):
        """Test _is_async_evaluation function."""
        from dotevals.evaluation import Evaluation

        # Test sync function
        sync_item = MagicMock()
        mock_eval = MagicMock(spec=Evaluation)
        mock_eval.eval_fn = lambda: None
        sync_item.function = mock_eval
        assert not _is_async_evaluation(sync_item)

        # Test async function
        async_item = MagicMock()

        async def async_fn():
            pass

        mock_async_eval = MagicMock(spec=Evaluation)
        mock_async_eval.eval_fn = async_fn
        async_item.function = mock_async_eval
        assert _is_async_evaluation(async_item)

        # Test non-Evaluation object
        invalid_item = MagicMock()
        invalid_item.function = lambda: None
        with pytest.raises(TypeError, match="Expected Evaluation object"):
            _is_async_evaluation(invalid_item)

    def test_is_async_evaluation_edge_cases(self):
        """Test _is_async_evaluation with various edge cases."""
        # Test with object that has no function attribute
        item = MagicMock()
        del item.function  # Remove function attribute
        with pytest.raises(AttributeError):
            _is_async_evaluation(item)

        # Test with non-Evaluation object
        item2 = MagicMock()
        item2.function = "not_an_evaluation"
        with pytest.raises(TypeError, match="Expected Evaluation object"):
            _is_async_evaluation(item2)


class TestProgressManager:
    """Test progress manager integration."""

    @pytest.mark.asyncio
    async def test_empty_evaluation_list_progress(self):
        """Test that progress manager handles empty evaluation list."""
        runner = Runner()

        # Spy on progress manager
        with patch.object(runner.progress_manager, "start") as mock_start:
            with patch.object(runner.progress_manager, "finish") as mock_finish:
                # Run with empty list
                await runner.run_evaluations([])

                # Progress manager should not be called for empty list
                mock_start.assert_not_called()
                mock_finish.assert_not_called()


class TestRunnerIntegration:
    """Integration tests for the runner system."""

    @pytest.mark.asyncio
    async def test_runner_initialization(self):
        """Test Runner initialization with parameters."""
        runner = Runner(experiment_name="exp1", samples=10, concurrent=False)
        assert runner.experiment_name == "exp1"
        assert runner.samples == 10
        assert runner.concurrent is False

        # Test with defaults
        runner2 = Runner()
        assert runner2.experiment_name is None
        assert runner2.samples is None
        assert runner2.concurrent is True

    @pytest.mark.asyncio
    async def test_sync_function_returns_coroutine(self):
        """Test that a sync function returning a coroutine is handled correctly."""
        results = {}
        runner = Runner(results_dict=results)

        # Create a sync function that returns a coroutine
        async def async_result():
            await asyncio.sleep(0.01)

            return EvaluationSummary([])

        def sync_func_returning_coroutine(session_manager, samples, progress_manager):
            # This sync function returns a coroutine object
            return async_result()

        # Create mock item
        item = MagicMock()
        item.name = "test_eval"
        item.function = create_mock_evaluation(sync_func_returning_coroutine)
        item.fixtures = {}

        # Run the evaluation
        await runner.run_evaluations([item])

        # Verify the coroutine was awaited and result stored
        assert "test_eval" in results
        assert isinstance(results["test_eval"], EvaluationSummary)

    @pytest.mark.asyncio
    async def test_runner_exception_handling(self):
        """Test runner handles exceptions during evaluation."""
        with tempfile.TemporaryDirectory():
            runner = Runner()
            results = {}
            runner.results = results

            # Create an evaluation that will have an error
            # Using a real evaluation with a dataset that causes errors
            @foreach("value", [(1,), (0,)])  # 0 will cause division by zero
            def eval_with_error(value):
                if value == 0:
                    raise ValueError("Test error")
                from dotevals.evaluators import exact_match
                from dotevals.results import Result

                return Result(exact_match(1 / value, 1))  # This will fail on value=0

            # Create mock item
            mock_item = MagicMock()
            mock_item.name = "test_eval"
            mock_item.function = eval_with_error

            # Run evaluation - exceptions are now handled internally by executor
            await runner._run_single_evaluation(mock_item)

            # Verify the result was stored and contains error
            assert "test_eval" in results
            summary = results["test_eval"]
            # Should have 2 results: one success, one error
            assert len(summary.results) == 2
            errors = [r for r in summary.results if r.error]
            assert len(errors) == 1
            assert "ValueError: Test error" in errors[0].error

    def test_runner_default_initialization(self):
        """Test runner initialization with defaults."""
        runner = Runner()

        assert runner.experiment_name is None
        assert runner.samples is None
        assert runner.concurrent is True  # Default value
        assert runner.results == {}
        assert runner.progress_manager is not None
