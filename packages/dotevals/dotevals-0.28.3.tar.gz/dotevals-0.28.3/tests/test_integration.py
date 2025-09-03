"""Parametrized integration tests for complete dotevals workflows."""

import asyncio
from pathlib import Path

import pytest

from dotevals import ForEach, Result, batch, foreach
from dotevals.evaluators import exact_match
from dotevals.results import Score
from dotevals.sessions import SessionManager, get_default_session_manager
from dotevals.storage.json import JSONStorage


class TestForEachIntegration:
    """Parametrized integration tests for @foreach decorator."""

    @pytest.mark.parametrize(
        "is_async,dataset,expected_scores",
        [
            # Sync basic test
            (
                False,
                [
                    {"input": "hello", "expected": "HELLO"},
                    {"input": "world", "expected": "WORLD"},
                ],
                [True, True],
            ),
            # Async basic test
            (True, [{"x": 1}, {"x": 2}, {"x": 3}], [2.0, 4.0, 6.0]),
            # Sync with sentiment scoring
            (
                False,
                [{"text": "positive"}, {"text": "negative"}, {"text": "neutral"}],
                [1.0, 0.0, 0.5],
            ),
        ],
        ids=["sync_basic", "async_double", "sync_sentiment"],
    )
    def test_foreach_evaluation(self, is_async, dataset, expected_scores):
        """Test foreach evaluation with various datasets and scoring functions."""
        session_manager = get_default_session_manager()

        if is_async:
            # Async double function
            @foreach("x", dataset)
            async def eval_fn(x: int) -> Score:
                await asyncio.sleep(0.01)  # Simulate async work
                return Score(name="double", value=float(x * 2), metrics=[])

            summary = asyncio.run(eval_fn(session_manager, samples=None))
            values = sorted([r.scores[0].value for r in summary.results])
            assert values == expected_scores
        else:
            if "expected" in dataset[0]:
                # Uppercase matching
                @foreach("input,expected", dataset)
                def eval_fn(input: str, expected: str) -> Score:
                    return Score(
                        name="uppercase_match",
                        value=input.upper() == expected,
                        metrics=[],
                    )

                summary = asyncio.run(eval_fn(session_manager, samples=None))
                assert all(
                    r.scores[0].value == exp
                    for r, exp in zip(summary.results, expected_scores)
                )
            else:
                # Sentiment scoring
                @foreach("text", dataset)
                def eval_fn(text: str) -> Score:
                    sentiment_scores = {
                        "positive": 1.0,
                        "negative": 0.0,
                        "neutral": 0.5,
                    }
                    return Score(
                        name="sentiment",
                        value=sentiment_scores.get(text, 0.5),
                        metrics=[],
                    )

                summary = asyncio.run(eval_fn(session_manager, samples=None))
                scores = [r.scores[0].value for r in summary.results]
                assert scores == expected_scores

    @pytest.mark.parametrize(
        "dataset,error_indices",
        [
            ([{"value": 10}, {"value": 0}, {"value": 5}], [1]),  # Division by zero
            (
                [{"value": 1}, {"value": -1}, {"value": 0}, {"value": 2}],
                [2],
            ),  # Zero at index 2
            ([{"value": 0}], [0]),  # Single error
        ],
        ids=["middle_error", "third_error", "single_error"],
    )
    def test_foreach_error_handling(self, dataset, error_indices):
        """Test foreach error handling with various error positions."""

        @foreach("value", dataset)
        def divide_eval(value: int) -> Score:
            result = 100 / value
            return Score(name="division", value=result, metrics=[])

        session_manager = get_default_session_manager()
        summary = asyncio.run(divide_eval(session_manager, samples=None))

        assert len(summary.results) == len(dataset)

        # Check errors at expected indices
        for i, result in enumerate(summary.results):
            if i in error_indices:
                assert result.error is not None
                assert "ZeroDivisionError" in result.error
            else:
                assert result.error is None
                assert result.scores[0].value == 100 / dataset[i]["value"]


class TestBatchIntegration:
    """Parametrized integration tests for @batch decorator."""

    @pytest.mark.parametrize(
        "is_async,dataset_size,batch_size",
        [
            (False, 5, 2),  # Sync with uneven batches
            (False, 6, 3),  # Sync with even batches
            (True, 6, 3),  # Async with even batches
            (False, 10, 10),  # Single batch
            (False, 3, 1),  # Batch size of 1
        ],
        ids=["sync_uneven", "sync_even", "async_even", "single_batch", "batch_size_1"],
    )
    def test_batch_evaluation(self, is_async, dataset_size, batch_size):
        """Test batch evaluation with various configurations."""
        dataset = [{"value": i + 1} for i in range(dataset_size)]
        session_manager = get_default_session_manager()

        if is_async:

            @batch("value", dataset, batch_size=batch_size)
            async def eval_fn(value: list[int]) -> list[Score]:
                await asyncio.sleep(0.01)
                return [
                    Score(name="double", value=float(v * 2), metrics=[]) for v in value
                ]

            summary = asyncio.run(eval_fn(session_manager, samples=None))
        else:

            @batch("value", dataset, batch_size=batch_size)
            def eval_fn(value: list[int]) -> list[Score]:
                return [
                    Score(name="double", value=float(v * 2), metrics=[]) for v in value
                ]

            summary = asyncio.run(eval_fn(session_manager, samples=None))

        # Verify all items processed
        assert len(summary.results) == dataset_size

        # Verify correct values
        values = [r.scores[0].value for r in summary.results]
        expected = [float((i + 1) * 2) for i in range(dataset_size)]
        assert values == expected

    @pytest.mark.parametrize(
        "dataset,batch_size,error_batch_indices",
        [
            ([{"v": 2}, {"v": 0}, {"v": 3}, {"v": 4}], 2, [0]),  # First batch has error
            (
                [{"v": 1}, {"v": 2}, {"v": 0}, {"v": 3}],
                2,
                [1],
            ),  # Second batch has error
            (
                [{"v": 0}, {"v": 0}, {"v": 1}, {"v": 2}],
                2,
                [0],
            ),  # First batch all errors
        ],
        ids=["first_batch_error", "second_batch_error", "full_batch_error"],
    )
    def test_batch_error_handling(self, dataset, batch_size, error_batch_indices):
        """Test batch error handling with errors in different batches."""

        @batch("v", dataset, batch_size=batch_size)
        def divide_batch(v: list[int]) -> list[Score]:
            return [Score(name="div", value=10 / val, metrics=[]) for val in v]

        session_manager = get_default_session_manager()
        summary = asyncio.run(divide_batch(session_manager, samples=None))

        assert len(summary.results) == len(dataset)

        # Check which batches had errors
        for batch_idx in range(0, len(dataset), batch_size):
            batch_num = batch_idx // batch_size
            batch_results = summary.results[batch_idx : batch_idx + batch_size]

            if batch_num in error_batch_indices:
                # This batch should have errors
                assert all(r.error is not None for r in batch_results)
            else:
                # This batch should succeed
                for i, r in enumerate(batch_results):
                    assert r.error is None
                    assert r.scores[0].value == 10 / dataset[batch_idx + i]["v"]


class TestDecoratorComparison:
    """Parametrized tests comparing foreach and batch decorators."""

    @pytest.mark.parametrize(
        "decorator_type,dataset",
        [
            (foreach, []),  # Empty foreach
            (batch, []),  # Empty batch
            (foreach, [{"value": 1}]),  # Single item foreach
            (batch, [{"value": 1}]),  # Single item batch
        ],
        ids=["foreach_empty", "batch_empty", "foreach_single", "batch_single"],
    )
    def test_edge_cases(self, decorator_type, dataset):
        """Test edge cases for both decorators."""
        session_manager = get_default_session_manager()

        if decorator_type == foreach:

            @decorator_type("value", dataset)
            def eval_fn(value: int) -> Score:
                return Score(name="test", value=float(value), metrics=[])
        else:  # batch

            @decorator_type("value", dataset, batch_size=10)
            def eval_fn(value: list[int]) -> list[Score]:
                return [Score(name="test", value=float(v), metrics=[]) for v in value]

        summary = asyncio.run(eval_fn(session_manager, samples=None))
        assert len(summary.results) == len(dataset)


class TestWorkflowIntegration:
    """Parametrized tests for complete evaluation workflows."""

    @pytest.mark.parametrize(
        "experiment_name,num_evaluations,num_results_each",
        [
            ("single_eval", 1, 3),
            ("multi_eval", 3, 2),
            ("large_eval", 1, 10),
        ],
        ids=["single", "multiple", "large"],
    )
    def test_complete_workflow(
        self, tmp_path, experiment_name, num_evaluations, num_results_each
    ):
        """Test complete evaluation workflow with persistence."""
        storage_path = Path(tmp_path)

        # Create and run evaluations
        for eval_idx in range(num_evaluations):
            test_data = [(f"Q{i}", f"A{i}") for i in range(num_results_each)]

            foreach_inst = ForEach()

            @foreach_inst("question,answer", test_data)
            def eval_fn(question, answer):
                prompt = f"Question: {question}"
                result = answer if "1" in question else "wrong"
                return Result(exact_match(result, answer), prompt=prompt)

            session_manager = SessionManager(
                storage=f"json://{storage_path}",
                experiment_name=experiment_name,
                evaluation_name=f"eval_{eval_idx}",
            )

            summary = asyncio.run(eval_fn(session_manager, samples=None))
            assert len(summary.results) == num_results_each

        # Verify persistence
        storage = JSONStorage(storage_path)
        experiments = storage.list_experiments()
        assert experiment_name in experiments

        evaluations = storage.list_evaluations(experiment_name)
        assert len(evaluations) == num_evaluations

        # Check all results persisted
        for eval_idx in range(num_evaluations):
            results = storage.get_results(experiment_name, f"eval_{eval_idx}")
            assert len(results) == num_results_each

    @pytest.mark.parametrize(
        "resume_after,total_items",
        [
            (2, 5),  # Resume after 2 of 5
            (0, 3),  # Resume from beginning
            (4, 4),  # Already complete
        ],
        ids=["partial", "from_start", "complete"],
    )
    def test_evaluation_resumption(self, tmp_path, resume_after, total_items):
        """Test evaluation resumption from different states."""
        storage_path = Path(tmp_path)
        test_data = [(f"Q{i}", f"A{i}") for i in range(total_items)]

        # First run - process only 'resume_after' items
        if resume_after > 0:
            foreach_inst = ForEach()

            @foreach_inst("question,answer", test_data[:resume_after])
            def eval_fn(question, answer):
                return Result(exact_match(answer, answer), prompt=f"Q: {question}")

            session_manager = SessionManager(
                storage=f"json://{storage_path}",
                experiment_name="resume_test",
                evaluation_name="eval1",
            )

            asyncio.run(eval_fn(session_manager, samples=None))

        # Second run - should skip already processed items
        foreach_inst = ForEach()

        @foreach_inst("question,answer", test_data)
        def eval_fn_resume(question, answer):
            return Result(exact_match(answer, answer), prompt=f"Q: {question}")

        session_manager = SessionManager(
            storage=f"json://{storage_path}",
            experiment_name="resume_test",
            evaluation_name="eval1",
        )

        asyncio.run(eval_fn_resume(session_manager, samples=None))

        # Check correct number of results
        storage = JSONStorage(storage_path)
        results = storage.get_results("resume_test", "eval1")

        # Should have all items (either from first run or completed in second)
        assert len(results) >= min(resume_after, total_items)
