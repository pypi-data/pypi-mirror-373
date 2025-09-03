"""Tests for base storage interface."""

import pytest

from dotevals.storage.base import Storage


class TestStorageInterface:
    """Test the Storage abstract base class."""

    def test_storage_is_abstract(self):
        """Test that Storage cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            Storage()

    def test_storage_abstract_methods(self):
        """Test that Storage defines required abstract methods."""

        # Create a concrete implementation that doesn't implement all methods
        class IncompleteStorage(Storage):
            def create_experiment(self, experiment_name):
                pass

        # Should fail because not all abstract methods are implemented
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteStorage()

    def test_storage_concrete_implementation(self):
        """Test that a complete Storage implementation can be instantiated."""

        class ConcreteStorage(Storage):
            def create_experiment(self, experiment_name):
                pass

            def list_experiments(self):
                return []

            def delete_experiment(self, experiment_name):
                pass

            def rename_experiment(self, old_name, new_name):
                pass

            def create_evaluation(self, experiment_name, evaluation):
                pass

            def list_evaluations(self, experiment_name):
                return []

            def load_evaluation(self, experiment_name, evaluation_name):
                return None

            def update_evaluation_status(
                self, experiment_name, evaluation_name, status
            ):
                pass

            def add_results(self, experiment_name, evaluation_name, results):
                pass

            def get_results(self, experiment_name, evaluation_name):
                return []

            def completed_items(self, experiment_name, evaluation_name):
                return []

            def remove_error_results_batch(
                self, experiment_name, evaluation_name, item_ids
            ):
                pass

            def remove_error_result(self, experiment_name, evaluation_name, item_id):
                pass

        # Should be able to instantiate
        storage = ConcreteStorage()
        assert isinstance(storage, Storage)

    def test_storage_interface_methods(self):
        """Test that Storage interface has expected method signatures."""
        # Check that Storage defines the expected abstract methods
        expected_methods = {
            "create_experiment",
            "list_experiments",
            "delete_experiment",
            "rename_experiment",
            "create_evaluation",
            "list_evaluations",
            "load_evaluation",
            "update_evaluation_status",
            "add_results",
            "get_results",
            "completed_items",
            "remove_error_result",  # This is the abstract method, not remove_error_results_batch
        }

        # All expected methods should be in abstract methods
        for method in expected_methods:
            assert hasattr(Storage, method), f"Storage should have {method} method"

    def test_remove_error_results_batch_default_implementation(self):
        """Test that remove_error_results_batch has a default implementation."""

        # Create a concrete implementation
        class ConcreteStorage(Storage):
            def __init__(self):
                self.removed_items = []

            def create_experiment(self, experiment_name):
                pass

            def list_experiments(self):
                return []

            def delete_experiment(self, experiment_name):
                pass

            def rename_experiment(self, old_name, new_name):
                pass

            def create_evaluation(self, experiment_name, evaluation):
                pass

            def list_evaluations(self, experiment_name):
                return []

            def load_evaluation(self, experiment_name, evaluation_name):
                return None

            def update_evaluation_status(
                self, experiment_name, evaluation_name, status
            ):
                pass

            def add_results(self, experiment_name, evaluation_name, results):
                pass

            def get_results(self, experiment_name, evaluation_name):
                return []

            def completed_items(self, experiment_name, evaluation_name):
                return []

            def remove_error_result(self, experiment_name, evaluation_name, item_id):
                # Track which items were removed
                self.removed_items.append(item_id)

        storage = ConcreteStorage()

        # Call the default implementation of remove_error_results_batch
        storage.remove_error_results_batch("exp1", "eval1", [1, 2, 3])

        # Verify it called remove_error_result for each item
        assert storage.removed_items == [1, 2, 3]
