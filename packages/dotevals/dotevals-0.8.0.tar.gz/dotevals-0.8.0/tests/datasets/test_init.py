"""Tests for datasets module dynamic imports."""

import pytest

from dotevals import datasets
from dotevals.datasets import Dataset, registry


class TestDatasetsModuleDynamicImports:
    """Test dynamic imports and attribute access in datasets module."""

    def test_getattr_existing_dataset(self, monkeypatch):
        """Test __getattr__ for existing dataset."""

        # Mock a dataset class
        class MockDataset(Dataset):
            columns = ["input", "output"]

            def __init__(self, split=None):
                super().__init__(split)

            def __iter__(self):
                yield {"input": "test", "output": "result"}

        # Mock the registry to return our dataset
        def mock_get_dataset_class(name):
            if name == "mock_dataset":
                return MockDataset
            raise ValueError(f"Unknown dataset: {name}")

        monkeypatch.setattr(registry, "get_dataset_class", mock_get_dataset_class)

        # Test dynamic import
        dataset_class = datasets.__getattr__("mock_dataset")
        assert dataset_class is MockDataset

        # Test that we can instantiate it
        dataset = dataset_class()
        assert isinstance(dataset, Dataset)

    def test_getattr_non_existent_dataset(self):
        """Test __getattr__ for non-existent dataset."""
        with pytest.raises(
            AttributeError,
            match="module 'dotevals.datasets' has no attribute 'non_existent'",
        ):
            datasets.__getattr__("non_existent")

    def test_dir_includes_datasets(self, monkeypatch):
        """Test __dir__ includes registered datasets."""

        # Mock the registry to return some dataset names
        def mock_list_datasets():
            return ["dataset1", "dataset2", "dataset3"]

        monkeypatch.setattr(registry, "list_datasets", mock_list_datasets)

        # Get the directory listing
        dir_result = datasets.__dir__()

        # Check that core exports are included
        assert "Dataset" in dir_result
        assert "registry" in dir_result
        assert "list_available" in dir_result
        assert "get_dataset_info" in dir_result

        # Check that dataset names are included
        assert "dataset1" in dir_result
        assert "dataset2" in dir_result
        assert "dataset3" in dir_result

    def test_import_syntax_works(self, monkeypatch):
        """Test that import syntax works with dynamic attributes."""

        # Mock a dataset class
        class TestDataset(Dataset):
            columns = ["text"]

            def __init__(self, split=None):
                super().__init__(split)

            def __iter__(self):
                yield {"text": "sample"}

        # Mock the registry
        def mock_get_dataset_class(name):
            if name == "test_dataset":
                return TestDataset
            raise ValueError(f"Unknown dataset: {name}")

        monkeypatch.setattr(registry, "get_dataset_class", mock_get_dataset_class)

        # Test accessing via getattr (simulating `from dotevals.datasets import test_dataset`)
        TestDatasetClass = getattr(datasets, "test_dataset")
        assert TestDatasetClass is TestDataset

        # Create instance and verify it works
        instance = TestDatasetClass()
        data = list(instance)
        assert len(data) == 1
        assert data[0] == {"text": "sample"}

    def test_attribute_error_converts_properly(self, monkeypatch):
        """Test that ValueError from registry is converted to AttributeError."""

        # Mock the registry to raise ValueError
        def mock_get_dataset_class(name):
            raise ValueError(f"Unknown dataset: {name}")

        monkeypatch.setattr(registry, "get_dataset_class", mock_get_dataset_class)

        # Should raise AttributeError, not ValueError
        with pytest.raises(AttributeError) as exc_info:
            getattr(datasets, "unknown_dataset")

        assert "module 'dotevals.datasets' has no attribute 'unknown_dataset'" in str(
            exc_info.value
        )

    def test_dir_returns_combined_list(self, monkeypatch):
        """Test that __dir__ returns combined list of core exports and datasets."""

        # Mock the registry
        def mock_list_datasets():
            return ["custom1", "custom2"]

        monkeypatch.setattr(registry, "list_datasets", mock_list_datasets)

        result = datasets.__dir__()

        # Should be a list
        assert isinstance(result, list)

        # Should contain both core exports and dataset names
        core_exports = ["Dataset", "registry", "list_available", "get_dataset_info"]
        for export in core_exports:
            assert export in result

        assert "custom1" in result
        assert "custom2" in result

        # Should not have duplicates
        assert len(result) == len(set(result))
