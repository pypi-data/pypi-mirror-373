"""Tests for the interactive API."""

from unittest.mock import Mock

import pytest

from dotevals import foreach
from dotevals.evaluators import exact_match
from dotevals.interactive import Results, run
from dotevals.storage.json import JSONStorage


class TestInteractiveRun:
    """Test the run() function."""

    def test_run_basic_evaluation(self, tmp_path):
        """Test running a basic evaluation."""
        # Create a simple dataset
        dataset = [
            ("2 + 2", "4"),
            ("3 + 3", "6"),
        ]

        # Define evaluation function
        @foreach("question,answer", dataset)
        def eval_math(question, answer, model):
            # Mock model that returns correct answers
            return exact_match(model.generate(question), answer)

        # Create mock model
        mock_model = Mock()
        mock_model.generate.side_effect = ["4", "6"]

        # Run evaluation
        results = run(
            eval_math,
            experiment="test_exp",
            storage=f"json://{tmp_path}",
            model=mock_model,
        )

        # Check results
        assert isinstance(results, Results)
        assert results.experiment == "test_exp"
        assert results.evaluation == "eval_math"

        # Check summary
        summary = results.summary()
        assert summary["total"] == 2
        assert summary["errors"] == 0
        assert "exact_match" in summary["metrics"]
        assert summary["metrics"]["exact_match"]["accuracy"] == 1.0

    def test_run_with_errors(self, tmp_path):
        """Test running evaluation with errors."""
        dataset = [
            ("2 + 2", "4"),
            ("3 + 3", "6"),
        ]

        @foreach("question,answer", dataset)
        def eval_with_error(question, answer, model):
            if question == "3 + 3":
                raise ValueError("Test error")
            return exact_match(model.generate(question), answer)

        mock_model = Mock()
        mock_model.generate.return_value = "4"

        results = run(eval_with_error, storage=f"json://{tmp_path}", model=mock_model)

        summary = results.summary()
        assert summary["total"] == 2
        assert summary["errors"] == 1
        assert summary["metrics"]["exact_match"]["accuracy"] == 0.5

    def test_run_auto_generates_experiment_name(self, tmp_path):
        """Test that experiment name is auto-generated if not provided."""
        dataset = [("test", "test")]

        @foreach("input,expected", dataset)
        def eval_simple(input, expected, model):
            return exact_match(input, expected)

        results = run(eval_simple, storage=f"json://{tmp_path}", model=Mock())

        assert results.experiment.startswith("run_")
        assert len(results.experiment) > 10  # Should have timestamp

    def test_run_with_limit(self, tmp_path):
        """Test running with sample limit."""
        dataset = [
            ("1", "1"),
            ("2", "2"),
            ("3", "3"),
            ("4", "4"),
            ("5", "5"),
        ]

        @foreach("input,expected", dataset)
        def eval_limited(input, expected):
            return exact_match(input, expected)

        results = run(eval_limited, samples=3, storage=f"json://{tmp_path}")

        summary = results.summary()
        assert summary["total"] == 3  # Should only process 3 samples

    def test_run_requires_decorated_function(self, tmp_path):
        """Test that run() requires a decorated function."""

        def undecorated_function(question, answer, model):
            return exact_match("test", "test")

        with pytest.raises(ValueError, match="must be decorated with @foreach"):
            run(undecorated_function, storage=f"json://{tmp_path}", model=Mock())

    def test_run_with_kwargs(self, tmp_path):
        """Test passing additional kwargs to evaluation function."""
        dataset = [("test", "test")]

        @foreach("input,expected", dataset)
        def eval_with_params(input, expected, model, temperature, max_tokens):
            # Check that parameters are passed through
            assert temperature == 0.7
            assert max_tokens == 100
            return exact_match(input, expected)

        results = run(
            eval_with_params,
            storage=f"json://{tmp_path}",
            model=Mock(),
            temperature=0.7,
            max_tokens=100,
        )

        summary = results.summary()
        assert summary["total"] == 1
        assert summary["errors"] == 0

    def test_run_with_async_function(self, tmp_path):
        """Test running async evaluation function."""
        dataset = [("test", "test")]

        @foreach("input,expected", dataset)
        async def eval_async(input, expected):
            # Async evaluation function
            return exact_match(input, expected)

        # Both sync and async functions are handled the same way
        results = run(eval_async, storage=f"json://{tmp_path}")

        summary = results.summary()
        assert summary["total"] == 1
        assert summary["errors"] == 0
        assert summary["metrics"]["exact_match"]["accuracy"] == 1.0

    def test_run_with_custom_storage(self, tmp_path):
        """Test using custom storage backend."""
        dataset = [("test", "test")]

        @foreach("input,expected", dataset)
        def eval_storage(input, expected):
            return exact_match(input, expected)

        # Test with storage instance
        storage = JSONStorage(str(tmp_path))
        results = run(eval_storage, experiment="custom_storage_test", storage=storage)

        assert results.storage is storage
        assert results.experiment == "custom_storage_test"

    def test_run_resumes_existing_evaluation(self, tmp_path):
        """Test that running with same experiment resumes."""
        dataset = [
            ("1", "1"),
            ("2", "2"),
            ("3", "3"),
        ]

        @foreach("input,expected", dataset)
        def eval_resume(input, expected):
            return exact_match(input, expected)

        # First run with limit
        results1 = run(
            eval_resume,
            experiment="resume_test",
            samples=2,
            storage=f"json://{tmp_path}",
        )
        assert results1.summary()["total"] == 2

        # Second run should resume
        results2 = run(
            eval_resume, experiment="resume_test", storage=f"json://{tmp_path}"
        )
        assert results2.summary()["total"] == 3  # Should have all 3 now

    def test_run_with_none_storage_uses_default(self, tmp_path):
        """Test that storage=None uses default json://.dotevals."""
        dataset = [("test", "test")]

        @foreach("input,expected", dataset)
        def eval_default_storage(input, expected):
            return exact_match(input, expected)

        # Run with storage=None to use default
        results = run(eval_default_storage, storage=None)

        # Should default to json://.dotevals
        assert results.storage is not None
        # Clean up the .dotevals directory after test
        import os
        import shutil

        if os.path.exists(".dotevals"):
            shutil.rmtree(".dotevals")


class TestResults:
    """Test the Results class."""

    def test_results_iteration(self, tmp_path):
        """Test that Results class is iterable over records."""
        dataset = [
            ("a", "a"),
            ("b", "b"),
            ("c", "x"),  # Wrong answer
        ]

        @foreach("input,expected", dataset)
        def eval_iter(input, expected):
            return exact_match(input, expected)

        results = run(eval_iter, storage=f"json://{tmp_path}")

        # Test iteration
        iterated_records = list(results)
        assert len(iterated_records) == 3
        assert iterated_records[0].item_id == 0
        assert iterated_records[1].item_id == 1
        assert iterated_records[2].item_id == 2

        # Test len
        assert len(results) == 3

        # Test indexing
        assert results[0].item_id == 0
        assert results[1].item_id == 1
        assert results[2].item_id == 2
        assert results[-1].item_id == 2

        # Test for loop
        ids = []
        for record in results:
            ids.append(record.item_id)
        assert ids == [0, 1, 2]

        # Test that we can filter by score value
        correct = [r for r in results if r.scores[0].value]
        incorrect = [r for r in results if not r.scores[0].value]
        assert len(correct) == 2
        assert len(incorrect) == 1

    def test_results_iteration_with_errors(self, tmp_path):
        """Test iteration over results with errors."""
        dataset = [
            ("a", "a"),
            ("b", "b"),
            ("c", "c"),
        ]

        @foreach("input,expected", dataset)
        def eval_with_errors(input, expected):
            if input == "b":
                raise ValueError("Test error")
            return exact_match(input, expected)

        results = run(eval_with_errors, storage=f"json://{tmp_path}")

        # Test that we can filter errors easily
        error_records = [r for r in results if r.error is not None]
        success_records = [r for r in results if r.error is None]

        assert len(error_records) == 1
        assert len(success_records) == 2
        assert error_records[0].item_id == 1
        assert "Test error" in error_records[0].error

    def test_results_lazy_loads_records(self, tmp_path):
        """Test that records are loaded lazily."""
        # Create evaluation data
        dataset = [("test", "test")]

        @foreach("input,expected", dataset)
        def eval_lazy(input, expected):
            return exact_match(input, expected)

        results = run(eval_lazy, storage=f"json://{tmp_path}")

        # Records should not be loaded yet
        assert results._records is None

        # Accessing records should load them
        records = results.records
        assert results._records is not None
        assert len(records) == 1

        # Second access should use cached records
        records2 = results.records
        assert records2 is records

    def test_results_summary_structure(self, tmp_path):
        """Test the structure of the summary."""
        dataset = [
            ("a", "a"),
            ("b", "b"),
            ("c", "x"),  # Wrong answer
        ]

        @foreach("input,expected", dataset)
        def eval_summary(input, expected):
            return exact_match(input, expected)

        results = run(eval_summary, storage=f"json://{tmp_path}")

        summary = results.summary()

        # Check structure
        assert "total" in summary
        assert "errors" in summary
        assert "metrics" in summary

        # Check values
        assert summary["total"] == 3
        assert summary["errors"] == 0
        assert summary["metrics"]["exact_match"]["accuracy"] == pytest.approx(2 / 3)

    def test_results_with_multiple_evaluators(self, tmp_path):
        """Test results with multiple evaluator scores."""
        from dotevals import Result

        dataset = [("test", "test")]

        @foreach("input,expected", dataset)
        def eval_multi(input, expected):
            return Result(
                exact_match(input, expected, name="exact"),
                exact_match(input.lower(), expected.lower(), name="case_insensitive"),
            )

        results = run(eval_multi, storage=f"json://{tmp_path}")

        summary = results.summary()
        assert "exact" in summary["metrics"]
        assert "case_insensitive" in summary["metrics"]
        assert summary["metrics"]["exact"]["accuracy"] == 1.0
        assert summary["metrics"]["case_insensitive"]["accuracy"] == 1.0

    def test_results_storage_access(self, tmp_path):
        """Test that Results provides access to storage."""
        dataset = [("test", "test")]

        @foreach("input,expected", dataset)
        def eval_storage_access(input, expected):
            return exact_match(input, expected)

        results = run(
            eval_storage_access, experiment="storage_test", storage=f"json://{tmp_path}"
        )

        # Should be able to access storage
        assert results.storage is not None
        assert isinstance(results.storage, JSONStorage)

        # Should be able to query storage directly
        experiments = results.storage.list_experiments()
        assert "storage_test" in experiments

    def test_results_empty_dataset(self, tmp_path):
        """Test Results with empty dataset."""
        dataset = []

        @foreach("input,expected", dataset)
        def eval_empty(input, expected):
            return exact_match(input, expected)

        results = run(eval_empty, storage=f"json://{tmp_path}")

        # Should handle empty dataset gracefully
        assert len(results) == 0
        assert list(results) == []

        summary = results.summary()
        assert summary["total"] == 0
        assert summary["errors"] == 0
        assert summary["metrics"] == {}

    def test_results_slicing(self, tmp_path):
        """Test that Results supports slicing operations."""
        dataset = [
            ("a", "a"),
            ("b", "b"),
            ("c", "c"),
            ("d", "d"),
            ("e", "e"),
        ]

        @foreach("input,expected", dataset)
        def eval_slice(input, expected):
            return exact_match(input, expected)

        results = run(eval_slice, storage=f"json://{tmp_path}")

        # Test various slicing operations
        slice_1_3 = results[1:3]
        assert len(slice_1_3) == 2
        assert slice_1_3[0].item_id == 1
        assert slice_1_3[1].item_id == 2

        # Test step slicing
        slice_step = results[::2]
        assert len(slice_step) == 3
        assert [r.item_id for r in slice_step] == [0, 2, 4]

        # Test negative slicing
        last_two = results[-2:]
        assert len(last_two) == 2
        assert [r.item_id for r in last_two] == [3, 4]


class TestInteractiveIntegration:
    """Integration tests for interactive mode."""

    def test_integration_with_real_dataset(self, tmp_path):
        """Test with a more realistic dataset."""
        # Simulate a real evaluation scenario
        qa_dataset = [
            ("What is the capital of France?", "Paris"),
            ("What is 2 + 2?", "4"),
            ("Who wrote Romeo and Juliet?", "Shakespeare"),
        ]

        @foreach("question,answer", qa_dataset)
        def eval_qa(question, answer, llm):
            response = llm.answer(question)
            return exact_match(response, answer)

        # Mock LLM
        mock_llm = Mock()
        mock_llm.answer.side_effect = [
            "Paris",
            "4",
            "William Shakespeare",
        ]  # Last one wrong

        results = run(
            eval_qa, experiment="qa_test", storage=f"json://{tmp_path}", llm=mock_llm
        )

        summary = results.summary()
        assert summary["total"] == 3
        assert summary["errors"] == 0
        assert summary["metrics"]["exact_match"]["accuracy"] == pytest.approx(2 / 3)

    def test_integration_notebook_workflow(self, tmp_path):
        """Test typical notebook workflow."""
        # Define dataset
        dataset = [
            ("positive", "positive"),
            ("negative", "negative"),
            ("neutral", "neutral"),
        ]

        # Define evaluation
        @foreach("text,label", dataset)
        def eval_sentiment(text, label, classifier):
            prediction = classifier.predict(text)
            return exact_match(prediction, label)

        # Create mock classifier
        classifier = Mock()
        classifier.predict.side_effect = [
            "positive",
            "negative",
            "positive",
        ]  # Last one wrong

        # Run evaluation
        results = run(
            eval_sentiment,
            experiment="sentiment_analysis",
            storage=f"json://{tmp_path}",
            classifier=classifier,
        )

        # Check results - typical notebook usage
        summary = results.summary()
        print(f"Accuracy: {summary['metrics']['exact_match']['accuracy']:.2%}")

        # Access records for debugging
        for record in results.records:
            if record.error:
                print(f"Error: {record.error}")
            else:
                print(f"Item {record.item_id}: {record.scores[0].value}")

        assert summary["metrics"]["exact_match"]["accuracy"] == pytest.approx(2 / 3)
