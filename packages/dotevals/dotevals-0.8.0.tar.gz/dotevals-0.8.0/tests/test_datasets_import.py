"""Tests for direct import of dataset classes from dotevals.datasets."""

from unittest.mock import patch

import pytest

from dotevals.datasets import Dataset
from dotevals.datasets.registry import DatasetRegistry


class MockGSM8K(Dataset):
    """Mock GSM8K dataset for testing."""

    name = "gsm8k"
    splits = ["train", "test"]
    columns = ["question", "reasoning", "answer"]
    num_rows = 1000

    def __init__(self, split="train", **kwargs):
        self.split = split
        self.kwargs = kwargs

    def __iter__(self):
        for i in range(3):
            yield f"Question {i}", f"Reasoning {i}", f"Answer {i}"


class MockBFCL(Dataset):
    """Mock BFCL dataset for testing."""

    name = "bfcl"
    splits = ["train", "validation", "test"]
    columns = ["function", "arguments", "expected"]
    num_rows = 500

    def __init__(self, split="test", **kwargs):
        self.split = split
        self.kwargs = kwargs

    def __iter__(self):
        for i in range(2):
            yield f"Function {i}", f"Args {i}", f"Expected {i}"


def test_direct_dataset_import():
    """Test that datasets can be imported directly from dotevals.datasets."""
    # Create a test registry with mock datasets
    test_registry = DatasetRegistry()
    test_registry.register(MockGSM8K)
    test_registry.register(MockBFCL)

    with patch("dotevals.datasets.registry", test_registry):
        # Import datasets by name
        from dotevals.datasets import bfcl, gsm8k

        # Verify they are the correct classes
        assert gsm8k is MockGSM8K
        assert bfcl is MockBFCL

        # Verify they can be instantiated
        gsm8k_instance = gsm8k(split="test")
        assert gsm8k_instance.split == "test"
        assert gsm8k_instance.name == "gsm8k"

        bfcl_instance = bfcl(split="validation")
        assert bfcl_instance.split == "validation"
        assert bfcl_instance.name == "bfcl"


def test_direct_dataset_import_not_found():
    """Test that importing non-existent dataset raises ImportError."""
    test_registry = DatasetRegistry()

    with patch("dotevals.datasets.registry", test_registry):
        with pytest.raises(ImportError, match="cannot import name 'nonexistent'"):
            from dotevals.datasets import nonexistent  # noqa: F401


def test_dataset_dir_includes_registered_datasets():
    """Test that __dir__ includes all registered dataset names."""
    test_registry = DatasetRegistry()
    test_registry.register(MockGSM8K)
    test_registry.register(MockBFCL)

    with patch("dotevals.datasets.registry", test_registry):
        import dotevals.datasets

        dir_contents = dir(dotevals.datasets)

        # Check that dataset names are included
        assert "gsm8k" in dir_contents
        assert "bfcl" in dir_contents

        # Check that core exports are also included
        assert "Dataset" in dir_contents
        assert "registry" in dir_contents
        assert "list_available" in dir_contents
        assert "get_dataset_info" in dir_contents


def test_dataset_import_with_usage():
    """Test that imported datasets can be used in real scenarios."""
    test_registry = DatasetRegistry()
    test_registry.register(MockGSM8K)

    with patch("dotevals.datasets.registry", test_registry):
        from dotevals.datasets import gsm8k

        # Create instance and iterate
        dataset = gsm8k(split="test")
        data = list(dataset)

        assert len(data) == 3
        assert data[0] == ("Question 0", "Reasoning 0", "Answer 0")
        assert data[-1] == ("Question 2", "Reasoning 2", "Answer 2")


def test_dataset_import_case_sensitivity():
    """Test that dataset import is case-sensitive."""
    test_registry = DatasetRegistry()
    test_registry.register(MockGSM8K)

    with patch("dotevals.datasets.registry", test_registry):
        # Lowercase works
        from dotevals.datasets import gsm8k

        assert gsm8k is MockGSM8K

        # Uppercase should fail (unless explicitly registered)
        with pytest.raises(ImportError):
            from dotevals.datasets import GSM8K  # noqa: F401
