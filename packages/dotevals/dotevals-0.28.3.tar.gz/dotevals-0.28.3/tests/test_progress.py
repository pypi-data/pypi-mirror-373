"""Tests for the progress module."""

import pytest

from dotevals.progress import BaseProgressManager, MultiProgress, SingleProgress
from dotevals.results import Record, Score


class TestBaseProgressManager:
    """Test the BaseProgressManager abstract class."""

    def test_base_progress_manager_is_abstract(self):
        """Test that BaseProgressManager cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            BaseProgressManager()

    def test_base_progress_manager_interface(self):
        """Test that BaseProgressManager defines required methods."""

        # Create a concrete implementation
        class ConcreteProgress(BaseProgressManager):
            def start_evaluation(self, name, total, dataset_info):
                pass

            def update_evaluation_progress(self, name, result):
                pass

            def finish(self):
                pass

        # Should be able to instantiate
        progress = ConcreteProgress()
        assert isinstance(progress, BaseProgressManager)


class TestProgressManagers:
    """Basic tests for progress managers."""

    def test_single_progress_instantiation(self):
        """Test that SingleProgress can be instantiated."""
        progress = SingleProgress()
        assert isinstance(progress, BaseProgressManager)

    def test_multi_progress_instantiation(self):
        """Test that MultiProgress can be instantiated."""
        progress = MultiProgress()
        assert isinstance(progress, BaseProgressManager)

    def test_single_progress_basic_workflow(self):
        """Test basic workflow with SingleProgress."""
        progress = SingleProgress()

        # Should be able to call required methods without error
        progress.start_evaluation("test", 10, {})

        result = Record(
            item_id=0,
            dataset_row={},
            scores=[Score("test", True, [])],
            prompt=None,
            model_response=None,
            error=None,
        )
        progress.update_evaluation_progress("test", result)

        progress.finish()

    def test_multi_progress_basic_workflow(self):
        """Test basic workflow with MultiProgress."""
        progress = MultiProgress()

        # Should be able to handle multiple evaluations
        progress.start_evaluation("eval1", 10, {})
        progress.start_evaluation("eval2", 20, {})

        result = Record(
            item_id=0,
            dataset_row={},
            scores=[Score("test", True, [])],
            prompt=None,
            model_response=None,
            error=None,
        )

        progress.update_evaluation_progress("eval1", result)
        progress.update_evaluation_progress("eval2", result)

        progress.finish()

    def test_progress_with_mixed_results(self):
        """Test progress with mixed success and error results."""
        progress = SingleProgress()

        # Should work with mixed results
        progress.start_evaluation("test", 100, {"name": "test_dataset"})

        for i in range(5):
            result = Record(
                item_id=i,
                dataset_row={},
                scores=[Score("test", i % 2 == 0, [])],
                prompt=None,
                model_response=None,
                error="Error" if i == 3 else None,
            )
            progress.update_evaluation_progress("test", result)

        progress.finish()

    def test_progress_handles_errors_gracefully(self):
        """Test that progress managers handle errors gracefully."""
        progress = SingleProgress()

        # Update without starting should not crash
        result = Record(
            item_id=0,
            dataset_row={},
            scores=[],
            prompt=None,
            model_response=None,
            error="Error",
        )

        # Should handle gracefully
        progress.update_evaluation_progress("nonexistent", result)
        progress.finish()
