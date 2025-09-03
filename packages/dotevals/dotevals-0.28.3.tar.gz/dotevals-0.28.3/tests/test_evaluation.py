"""Dedicated tests for the Evaluation class."""

import asyncio
from unittest.mock import MagicMock, patch

import pytest

from dotevals.evaluation import Evaluation
from dotevals.executors.batch import BatchExecutor
from dotevals.executors.foreach import ForEachExecutor
from dotevals.results import Result, Score
from dotevals.sessions import SessionManager


class TestEvaluation:
    """Test the Evaluation class."""

    def test_evaluation_initialization(self):
        """Test Evaluation initialization with all parameters."""
        eval_fn = lambda x: x
        dataset = [("a", 1), ("b", 2)]

        evaluation = Evaluation(
            eval_fn=eval_fn,
            dataset=dataset,
            executor_name="foreach",
            column_spec="text,number",
            executor_kwargs={"max_concurrency": 5},
            resolved_fixtures={"model": "test_model"},
        )

        assert evaluation.eval_fn == eval_fn
        assert evaluation.dataset == dataset
        assert evaluation.executor_name == "foreach"
        assert evaluation.column_spec == "text,number"
        assert evaluation.column_names == ["text", "number"]
        assert evaluation.executor_kwargs == {"max_concurrency": 5}
        assert evaluation.resolved_fixtures == {"model": "test_model"}

    def test_evaluation_column_names_parsing(self):
        """Test that column names are correctly parsed from column_spec."""
        evaluation = Evaluation(
            eval_fn=lambda: None,
            dataset=[],
            executor_name="foreach",
            column_spec="col1, col2,  col3 ",  # With spaces
            executor_kwargs={},
            resolved_fixtures={},
        )

        assert evaluation.column_names == ["col1", "col2", "col3"]

    def test_evaluation_get_executor_from_registry(self):
        """Test getting executor from registry."""
        mock_executor = MagicMock(spec=ForEachExecutor)

        with patch(
            "dotevals.evaluation.executor_registry.get", return_value=mock_executor
        ):
            evaluation = Evaluation(
                eval_fn=lambda: None,
                dataset=[],
                executor_name="custom_executor",
                column_spec="col",
                executor_kwargs={},
                resolved_fixtures={},
            )

            executor = evaluation._get_executor()
            assert executor == mock_executor

    def test_evaluation_get_executor_foreach_fallback(self):
        """Test falling back to ForEachExecutor when not in registry."""
        with patch("dotevals.evaluation.executor_registry.get", return_value=None):
            evaluation = Evaluation(
                eval_fn=lambda: None,
                dataset=[],
                executor_name="foreach",
                column_spec="col",
                executor_kwargs={},
                resolved_fixtures={},
            )

            executor = evaluation._get_executor()
            assert isinstance(executor, ForEachExecutor)

    def test_evaluation_get_executor_batch_fallback(self):
        """Test falling back to BatchExecutor when not in registry."""
        with patch("dotevals.evaluation.executor_registry.get", return_value=None):
            evaluation = Evaluation(
                eval_fn=lambda: None,
                dataset=[],
                executor_name="batch",
                column_spec="col",
                executor_kwargs={},
                resolved_fixtures={},
            )

            executor = evaluation._get_executor()
            assert isinstance(executor, BatchExecutor)

    def test_evaluation_get_executor_unknown_type(self):
        """Test error when executor type is unknown."""
        with patch("dotevals.evaluation.executor_registry.get", return_value=None):
            evaluation = Evaluation(
                eval_fn=lambda: None,
                dataset=[],
                executor_name="unknown_executor",
                column_spec="col",
                executor_kwargs={},
                resolved_fixtures={},
            )

            with pytest.raises(
                RuntimeError, match="Unknown executor type: unknown_executor"
            ):
                evaluation._get_executor()

    @pytest.mark.asyncio
    async def test_evaluation_call_with_session_manager(self, tmp_path):
        """Test calling evaluation with session manager."""

        # Create a simple evaluation function
        def eval_fn(text, number):
            return Result(Score("test", text == "a", []))

        dataset = [("a", 1), ("b", 2)]

        evaluation = Evaluation(
            eval_fn=eval_fn,
            dataset=dataset,
            executor_name="foreach",
            column_spec="text,number",
            executor_kwargs={},
            resolved_fixtures={},
        )

        session_manager = SessionManager(
            experiment_name="test_exp",
            evaluation_name="test_eval",
            storage=f"json://{tmp_path}",
        )

        # Call the evaluation
        summary = await evaluation(session_manager=session_manager, samples=None)

        # Check results
        assert len(summary.results) == 2
        assert summary.results[0].scores[0].value is True  # "a" == "a"
        assert summary.results[1].scores[0].value is False  # "b" != "a"

    @pytest.mark.asyncio
    async def test_evaluation_call_with_samples(self, tmp_path):
        """Test calling evaluation with samples parameter."""

        def eval_fn(value):
            return Result(Score("test", True, []))

        dataset = [(i,) for i in range(100)]

        evaluation = Evaluation(
            eval_fn=eval_fn,
            dataset=dataset,
            executor_name="foreach",
            column_spec="value",
            executor_kwargs={},
            resolved_fixtures={},
        )

        session_manager = SessionManager(
            experiment_name="test_exp",
            evaluation_name="test_eval",
            storage=f"json://{tmp_path}",
        )

        # Call with samples limit
        summary = await evaluation(session_manager=session_manager, samples=10)

        # Should only process 10 samples
        assert len(summary.results) == 10

    @pytest.mark.asyncio
    async def test_evaluation_call_with_kwargs(self, tmp_path):
        """Test calling evaluation with additional kwargs."""
        # Track kwargs received by executor
        received_kwargs = {}

        class TestExecutor(ForEachExecutor):
            async def execute(self, evaluation, session_manager, **kwargs):
                received_kwargs.update(kwargs)
                return await super().execute(evaluation, session_manager, **kwargs)

        mock_executor = TestExecutor()

        with patch(
            "dotevals.evaluation.executor_registry.get", return_value=mock_executor
        ):

            def eval_fn(value):
                return Result(Score("test", True, []))

            dataset = [(1,), (2,)]

            evaluation = Evaluation(
                eval_fn=eval_fn,
                dataset=dataset,
                executor_name="test_executor",
                column_spec="value",
                executor_kwargs={},
                resolved_fixtures={},
            )

            session_manager = SessionManager(
                experiment_name="test_exp",
                evaluation_name="test_eval",
                storage=f"json://{tmp_path}",
            )

            # Call with custom kwargs
            await evaluation(
                session_manager=session_manager,
                samples=None,
                custom_param="test_value",
                another_param=42,
            )

            # Check kwargs were passed through
            assert received_kwargs.get("custom_param") == "test_value"
            assert received_kwargs.get("another_param") == 42

    @pytest.mark.asyncio
    async def test_evaluation_with_resolved_fixtures(self, tmp_path):
        """Test evaluation with resolved fixtures."""
        # Track fixtures used
        fixtures_used = {}

        def eval_fn(value, model=None, temperature=None):
            fixtures_used["model"] = model
            fixtures_used["temperature"] = temperature
            return Result(Score("test", True, []))

        dataset = [(1,)]

        evaluation = Evaluation(
            eval_fn=eval_fn,
            dataset=dataset,
            executor_name="foreach",
            column_spec="value",
            executor_kwargs={},
            resolved_fixtures={"model": "gpt-4", "temperature": 0.7},
        )

        session_manager = SessionManager(
            experiment_name="test_exp",
            evaluation_name="test_eval",
            storage=f"json://{tmp_path}",
        )

        # The executor should merge resolved_fixtures with kwargs
        await evaluation(session_manager=session_manager, samples=None)

        # Fixtures should be passed to eval_fn
        assert fixtures_used["model"] == "gpt-4"
        assert fixtures_used["temperature"] == 0.7

    @pytest.mark.asyncio
    async def test_evaluation_with_async_eval_fn(self, tmp_path):
        """Test evaluation with async evaluation function."""

        async def async_eval_fn(value):
            await asyncio.sleep(0.001)  # Simulate async work
            return Result(Score("async_test", value > 0, []))

        dataset = [(1,), (0,), (2,)]

        evaluation = Evaluation(
            eval_fn=async_eval_fn,
            dataset=dataset,
            executor_name="foreach",
            column_spec="value",
            executor_kwargs={},
            resolved_fixtures={},
        )

        session_manager = SessionManager(
            experiment_name="test_exp",
            evaluation_name="test_eval",
            storage=f"json://{tmp_path}",
        )

        summary = await evaluation(session_manager=session_manager, samples=None)

        assert len(summary.results) == 3
        assert summary.results[0].scores[0].value is True  # 1 > 0
        assert summary.results[1].scores[0].value is False  # 0 > 0
        assert summary.results[2].scores[0].value is True  # 2 > 0

    @pytest.mark.asyncio
    async def test_evaluation_with_batch_executor(self, tmp_path):
        """Test evaluation with batch executor."""

        def batch_eval_fn(values):
            # Batch function receives lists
            return [Result(Score("batch_test", v > 0, [])) for v in values]

        dataset = [(1,), (0,), (2,), (3,)]

        evaluation = Evaluation(
            eval_fn=batch_eval_fn,
            dataset=dataset,
            executor_name="batch",
            column_spec="values",
            executor_kwargs={"batch_size": 2},
            resolved_fixtures={},
        )

        session_manager = SessionManager(
            experiment_name="test_exp",
            evaluation_name="test_eval",
            storage=f"json://{tmp_path}",
        )

        summary = await evaluation(session_manager=session_manager, samples=None)

        assert len(summary.results) == 4
        assert summary.results[0].scores[0].value is True  # 1 > 0
        assert summary.results[1].scores[0].value is False  # 0 > 0
        assert summary.results[2].scores[0].value is True  # 2 > 0
        assert summary.results[3].scores[0].value is True  # 3 > 0

    def test_evaluation_repr(self):
        """Test string representation of Evaluation."""
        evaluation = Evaluation(
            eval_fn=lambda x: x,
            dataset=[1, 2, 3],
            executor_name="foreach",
            column_spec="value",
            executor_kwargs={},
            resolved_fixtures={},
        )

        # Should have a meaningful representation
        repr_str = repr(evaluation)
        assert "Evaluation" in repr_str or "evaluation" in repr_str.lower()

    @pytest.mark.asyncio
    async def test_evaluation_empty_dataset(self, tmp_path):
        """Test evaluation with empty dataset."""

        def eval_fn(value):
            return Result(Score("test", True, []))

        evaluation = Evaluation(
            eval_fn=eval_fn,
            dataset=[],  # Empty dataset
            executor_name="foreach",
            column_spec="value",
            executor_kwargs={},
            resolved_fixtures={},
        )

        session_manager = SessionManager(
            experiment_name="test_exp",
            evaluation_name="test_eval",
            storage=f"json://{tmp_path}",
        )

        summary = await evaluation(session_manager=session_manager, samples=None)

        # Should handle empty dataset gracefully
        assert len(summary.results) == 0
        assert summary.summary == {}

    @pytest.mark.asyncio
    async def test_evaluation_with_error_in_eval_fn(self, tmp_path):
        """Test evaluation when eval function raises error."""

        def eval_fn(value):
            if value == 2:
                raise ValueError("Test error")
            return Result(Score("test", True, []))

        dataset = [(1,), (2,), (3,)]

        evaluation = Evaluation(
            eval_fn=eval_fn,
            dataset=dataset,
            executor_name="foreach",
            column_spec="value",
            executor_kwargs={},
            resolved_fixtures={},
        )

        session_manager = SessionManager(
            experiment_name="test_exp",
            evaluation_name="test_eval",
            storage=f"json://{tmp_path}",
        )

        summary = await evaluation(session_manager=session_manager, samples=None)

        # Should capture the error
        assert len(summary.results) == 3
        assert summary.results[0].error is None
        assert summary.results[1].error is not None
        assert "Test error" in summary.results[1].error
        assert summary.results[2].error is None
