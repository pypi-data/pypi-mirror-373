"""Dataset base class and plugin system for dotevals.

This module provides a plugin-based system for loading and managing datasets in
dotevals. Datasets can be registered via entry points, allowing third-party
packages to provide custom datasets that integrate seamlessly with dotevals's
decorators.
"""

from .base import Dataset, get_dataset_info, list_available
from .registry import registry

# Core exports
__all__ = ["Dataset", "registry", "list_available", "get_dataset_info"]


def __getattr__(name: str):
    """Dynamic attribute access for dataset classes.

    This allows importing dataset classes directly:
        >>> from dotevals.datasets import gsm8k
        >>> dataset = gsm8k(split="test")
    """
    # Try to get the dataset class
    try:
        return registry.get_dataset_class(name)
    except ValueError:
        # Convert ValueError to AttributeError for proper import behavior
        raise AttributeError(f"module 'dotevals.datasets' has no attribute '{name}'")


def __dir__():
    """List available attributes including all registered datasets.

    This enables tab completion for dataset classes.
    """
    # Get all dataset names as they are registered
    dataset_names = registry.list_datasets()

    return __all__ + dataset_names
