"""Tests for the dataset registry."""

from unittest.mock import MagicMock, patch

import pytest

from dotevals.datasets import Dataset, registry
from dotevals.datasets.registry import DatasetRegistry


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


class TestDatasetRegistry:
    """Test DatasetRegistry functionality."""

    def test_register_dataset(self):
        """Test registering a dataset."""
        registry = DatasetRegistry()
        registry.register(MockDataset)

        assert "mock_dataset" in registry._dataset_classes
        assert registry._dataset_classes["mock_dataset"] is MockDataset

    def test_register_duplicate_idempotent(self):
        """Test that re-registering the same class is idempotent."""
        registry = DatasetRegistry()
        registry.register(MockDataset)
        registry.register(MockDataset)  # Should not raise

        assert registry._dataset_classes["mock_dataset"] is MockDataset

    def test_register_duplicate_different_class_raises(self):
        """Test that registering a different class with the same name raises."""

        class AnotherMockDataset(Dataset):
            name = "mock_dataset"
            splits = []
            columns = []

            def __init__(self, split: str, **kwargs):
                pass

            def __iter__(self):
                pass

        registry = DatasetRegistry()
        registry.register(MockDataset)

        with pytest.raises(ValueError, match="already registered"):
            registry.register(AnotherMockDataset)

    def test_get_dataset_class(self):
        """Test retrieving a dataset class."""
        registry = DatasetRegistry()
        registry.register(MockDataset)

        dataset_class = registry.get_dataset_class("mock_dataset")
        assert dataset_class is MockDataset

    def test_get_dataset_class_not_found(self):
        """Test getting a non-existent dataset raises."""
        registry = DatasetRegistry()

        with pytest.raises(ValueError, match="Dataset 'nonexistent' not found"):
            registry.get_dataset_class("nonexistent")

    def test_list_datasets(self):
        """Test listing available datasets."""
        registry = DatasetRegistry()
        registry.register(MockDataset)

        datasets = registry.list_datasets()
        assert "mock_dataset" in datasets

    def test_registry_initialization(self):
        """Test DatasetRegistry initialization."""
        registry = DatasetRegistry()
        assert registry._dataset_classes == {}
        assert registry._discovery_completed is False


class TestDatasetPluginSystem:
    """Test dataset plugin discovery and loading."""

    def test_discover_plugins(self):
        """Test plugin discovery."""
        registry = DatasetRegistry()

        # Mock entry points
        mock_entry_point = MagicMock()
        mock_entry_point.load.return_value = MockDataset

        with patch("importlib.metadata.entry_points") as mock_ep:
            mock_ep.return_value = [mock_entry_point]
            registry.discover_plugins(force=True)

        assert "mock_dataset" in registry._dataset_classes

    def test_discover_plugins_invalid_dataset(self):
        """Test that invalid plugins are skipped with a warning."""
        registry = DatasetRegistry()

        # Create a class that doesn't inherit from Dataset
        class NotADataset:
            pass

        mock_entry_point = MagicMock()
        mock_entry_point.name = "bad_plugin"
        mock_entry_point.load.return_value = NotADataset

        with patch("importlib.metadata.entry_points") as mock_ep:
            mock_ep.return_value = [mock_entry_point]
            with pytest.warns(UserWarning, match="does not inherit from Dataset"):
                registry.discover_plugins(force=True)

        # Should not be registered
        assert len(registry._dataset_classes) == 0

    def test_discover_plugins_load_error(self):
        """Test that plugins that fail to load are skipped with a warning."""
        registry = DatasetRegistry()

        mock_entry_point = MagicMock()
        mock_entry_point.name = "error_plugin"
        mock_entry_point.load.side_effect = ImportError("Failed to import")

        with patch("importlib.metadata.entry_points") as mock_ep:
            mock_ep.return_value = [mock_entry_point]
            with pytest.warns(UserWarning, match="Failed to load plugin"):
                registry.discover_plugins(force=True)

        # Should not be registered
        assert len(registry._dataset_classes) == 0

    def test_discover_plugins_force(self):
        """Test that force=True re-discovers plugins."""
        registry = DatasetRegistry()

        # First discovery
        with patch("importlib.metadata.entry_points") as mock_ep:
            mock_ep.return_value = []
            registry.discover_plugins()

        assert registry._discovery_completed is True

        # Second discovery without force should not call entry_points again
        with patch("importlib.metadata.entry_points") as mock_ep:
            registry.discover_plugins()
            mock_ep.assert_not_called()

        # With force=True should re-discover
        mock_entry_point = MagicMock()
        mock_entry_point.load.return_value = MockDataset

        with patch("importlib.metadata.entry_points") as mock_ep:
            mock_ep.return_value = [mock_entry_point]
            registry.discover_plugins(force=True)
            mock_ep.assert_called_once()

        assert "mock_dataset" in registry._dataset_classes

    def test_discover_plugins_already_discovered_early_return(self):
        """Test that discover_plugins returns early if already discovered and not forced."""
        registry = DatasetRegistry()
        registry._discovery_completed = True

        with patch("importlib.metadata.entry_points") as mock_ep:
            registry.discover_plugins(force=False)
            # Should not even call entry_points
            mock_ep.assert_not_called()

    def test_discover_plugins_old_api(self):
        """Test the TypeError fallback path in discover_plugins."""
        registry = DatasetRegistry()

        # Create a mock that simulates old API behavior
        with patch("importlib.metadata.entry_points") as mock_ep:
            # First call raises TypeError (new API not supported)
            # Second call returns dict (old API)
            mock_ep.side_effect = [
                TypeError("entry_points() got an unexpected keyword argument 'group'"),
                {"dotevals.datasets": []},  # Old API returns dict
            ]

            registry.discover_plugins(force=True)
            assert registry._discovery_completed is True
            assert mock_ep.call_count == 2


def test_list_available():
    """Test list_available function."""
    from dotevals.datasets import list_available

    with patch.object(registry, "list_datasets", return_value=["dataset1", "dataset2"]):
        datasets = list_available()
        assert datasets == ["dataset1", "dataset2"]
