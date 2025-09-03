"""Tests for the Dataset base class."""

from unittest.mock import patch

import pytest

from dotevals.datasets import Dataset, get_dataset_info, registry


class MockDataset(Dataset):
    """Mock dataset for testing."""

    name = "mock_dataset"
    splits = ["train", "test"]
    columns = ["input", "output"]

    def __init__(self, split: str, **kwargs):
        self.split = split
        self.num_rows = 10

    def __iter__(self):
        for i in range(self.num_rows):
            yield (f"input_{i}", f"output_{i}")


class TestDatasetBase:
    """Test the Dataset base class."""

    def test_dataset_abstract_methods(self):
        """Test that Dataset enforces abstract methods."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            Dataset()

    def test_dataset_implementation(self):
        """Test a concrete dataset implementation."""
        dataset = MockDataset("train")

        assert dataset.split == "train"
        assert dataset.num_rows == 10

        # Test iteration
        items = list(dataset)
        assert len(items) == 10
        assert items[0] == ("input_0", "output_0")
        assert items[-1] == ("input_9", "output_9")

    def test_dataset_abstract_init(self):
        """Test that Dataset.__init__ is abstract."""

        # Create a dataset that doesn't implement __init__
        class BadDataset(Dataset):
            name = "bad"
            splits = []
            columns = []

            def __iter__(self):
                yield from []

        with pytest.raises(TypeError, match="abstract method"):
            BadDataset("train")

    def test_dataset_abstract_iter(self):
        """Test that Dataset.__iter__ is abstract."""

        # Create a dataset that doesn't implement __iter__
        class BadDataset(Dataset):
            name = "bad"
            splits = []
            columns = []

            def __init__(self, split: str, **kwargs):
                pass

        with pytest.raises(TypeError, match="abstract method"):
            BadDataset("train")


def test_get_dataset_info():
    """Test get_dataset_info function."""
    with patch.object(registry, "get_dataset_class", return_value=MockDataset):
        info = get_dataset_info("mock_dataset")

        assert info["name"] == "mock_dataset"
        assert info["splits"] == ["train", "test"]
        assert info["columns"] == ["input", "output"]
        assert info["num_rows"] is None  # MockDataset doesn't have class-level num_rows


def test_get_dataset_info_handles_missing_splits():
    """Test that get_dataset_info handles datasets without splits attribute."""

    # Create a dataset class without splits attribute
    class NoSplitsDataset(Dataset):
        name = "no_splits_test"
        columns = ["input", "output"]
        # No splits attribute defined

        def __init__(self, **kwargs):
            pass

        def __iter__(self):
            yield ("test", "output")

    # Mock the registry to return our test dataset
    with patch.object(registry, "get_dataset_class", return_value=NoSplitsDataset):
        info = get_dataset_info("no_splits_test")

        assert info["name"] == "no_splits_test"
        assert info["splits"] == []  # Should default to empty list
        assert info["columns"] == ["input", "output"]
        assert info["num_rows"] is None


def test_get_dataset_info_preserves_existing_splits():
    """Test that get_dataset_info preserves existing splits attribute."""

    # Create a dataset class with splits attribute
    class WithSplitsDataset(Dataset):
        name = "with_splits_test"
        splits = ["train", "test", "validation"]
        columns = ["question", "answer"]

        def __init__(self, split, **kwargs):
            self.split = split

        def __iter__(self):
            yield ("test question", "test answer")

    # Mock the registry to return our test dataset
    with patch.object(registry, "get_dataset_class", return_value=WithSplitsDataset):
        info = get_dataset_info("with_splits_test")

        assert info["name"] == "with_splits_test"
        assert info["splits"] == ["train", "test", "validation"]
        assert info["columns"] == ["question", "answer"]
        assert info["num_rows"] is None
