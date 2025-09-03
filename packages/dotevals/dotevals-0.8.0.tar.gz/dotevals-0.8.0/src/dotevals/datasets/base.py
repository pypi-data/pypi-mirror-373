"""Dataset base class and plugin system for dotevals.

This module provides a plugin-based system for loading and managing datasets
in dotevals. Datasets can be registered via entry points, allowing third-party
packages to provide custom datasets that integrate seamlessly with dotevals's
@foreach decorator.

The plugin system uses Python's entry points mechanism to discover and load
datasets at runtime. This allows for:
- Dynamic dataset discovery without modifying dotevals core
- Easy distribution of custom datasets as separate packages
- Lazy loading of dataset implementations

Examples:
    To use a registered dataset:

    ```python
    from dotevals import foreach

    @foreach.gsm8k("test")
    def eval_math(question, reasoning, answer, model):
        response = model.solve(question)
        return numeric_match(response, answer)
    ```

To create a custom dataset plugin, implement the Dataset ABC and register
it via entry points in your package's pyproject.toml.
"""

import warnings
from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Any


class Dataset(ABC):
    """Abstract base class for all dotevals datasets.

    All dataset plugins must inherit from this class and implement the required
    methods and attributes. Datasets are expected to be iterable and yield
    tuples of data that match the columns specification.

    Attributes:
        name: Unique identifier for the dataset (e.g., "gsm8k", "bfcl")
        splits: list of available data splits (e.g., ["train", "test", "validation"])
        columns: list of column names that will be yielded in order (e.g., ["question", "answer"])
        num_rows: Optional total number of rows in the dataset. Can be None for
                 streaming datasets or when the size is unknown.

    Examples:
        Creating a dataset with splits:

        ```python
        class MyDataset(Dataset):
            name = "my_dataset"
            splits = ["train", "test"]
            columns = ["input", "output"]

            def __init__(self, split: str | None = None, **kwargs):
                if split is None:
                    raise ValueError("This dataset requires a split")
                self.split = split
                self.data = self._load_data(split)
                self.num_rows = len(self.data)

            def __iter__(self):
                for item in self.data:
                    yield (item["input"], item["output"])
        ```

        Creating a dataset without splits:

        ```python
        class SimpleDataset(Dataset):
            name = "simple_dataset"
            splits = []  # No splits
            columns = ["question", "answer"]

            def __init__(self, split: str | None = None, **kwargs):
                # Ignore split parameter since this dataset has no splits
                self.data = self._load_all_data()
                self.num_rows = len(self.data)

            def __iter__(self):
                for item in self.data:
                    yield (item["question"], item["answer"])
        ```
    """

    name: str
    splits: list[str]
    columns: list[str]
    num_rows: int | None = None

    @abstractmethod
    def __init__(self, split: str | None = None, **kwargs: Any) -> None:
        """Initialize the dataset with the specified split.

        This method should load or prepare access to the dataset data.
        For large datasets, consider implementing lazy loading or streaming
        to avoid loading all data into memory at once.

        Args:
            split: The dataset split to load (must be one of the values in self.splits).
                  Can be None for datasets that don't have splits.
            **kwargs: Additional dataset-specific parameters

        Raises:
            ValueError: If the split is not valid for this dataset
            IOError: If the dataset files cannot be loaded
        """
        pass

    @abstractmethod
    def __iter__(self) -> Iterator[tuple]:
        """Iterate over dataset items.

        Each iteration should yield a tuple with values corresponding to
        the columns defined in self.columns. The order of values in the
        tuple must match the order of column names.

        Yields:
            tuple containing one value for each column in self.columns

        Examples:
            If self.columns = ["question", "answer"], then each yield
            should be a 2-tuple like ("What is 2+2?", "4")
        """
        pass

    def serialize_value(self, value: Any) -> Any:
        """Helper to serialize a single value for storage.

        This is a convenience method for datasets that need to convert
        complex types (like images, audio) to JSON-serializable formats
        during evaluation. Call this in your evaluation function if needed.

        Default implementation handles basic JSON types and common collections.
        Override _serialize_value to handle custom types.

        Example:
            # In your evaluation function
            serialized_image = dataset.serialize_value(image)
            return Result(..., metadata={"image": serialized_image})

        Args:
            value: Value to serialize

        Returns:
            JSON-serializable representation of value
        """
        return self._serialize_value(value)

    def deserialize_value(self, value: Any) -> Any:
        """Helper to deserialize a single value from storage.

        This is a convenience method to restore complex types that were
        serialized with serialize_value. Use this when loading results
        if you need to restore the original types.

        Args:
            value: Serialized value

        Returns:
            Deserialized value
        """
        return self._deserialize_value(value)

    def _serialize_value(self, value: Any) -> Any:
        """Serialize a single value. Override for custom types.

        Default implementation handles JSON-serializable types and
        converts complex types to string representation.

        Args:
            value: Value to serialize

        Returns:
            JSON-serializable representation of value
        """
        # Handle basic JSON-serializable types
        if isinstance(value, str | int | float | bool | type(None)):
            return value
        elif isinstance(value, dict):
            # Recursively serialize dict values
            return {k: self._serialize_value(v) for k, v in value.items()}
        elif isinstance(value, list | tuple):
            # Store type information for proper deserialization
            return {
                "__type__": type(value).__name__,
                "data": [self._serialize_value(v) for v in value],
            }
        elif isinstance(value, set):
            return {
                "__type__": "set",
                "data": [self._serialize_value(v) for v in value],
            }
        else:
            warnings.warn(f"Failed to serialize value {value}", UserWarning)
            return {
                "__type__": "str_fallback",
                "data": str(value),
                "class": f"{value.__class__.__module__}.{value.__class__.__name__}",
            }

    def _deserialize_value(self, value: Any) -> Any:
        """Deserialize a single value. Override for custom types.

        Args:
            value: Serialized value

        Returns:
            Deserialized value
        """
        if isinstance(value, dict) and "__type__" in value:
            type_name = value["__type__"]
            data = value["data"]

            if type_name == "list":
                return [self._deserialize_value(v) for v in data]
            elif type_name == "tuple":
                return tuple(self._deserialize_value(v) for v in data)
            elif type_name == "set":
                return {self._deserialize_value(v) for v in data}
            elif type_name == "str_fallback":
                # For unknown types that were stringified
                warnings.warn(
                    f"Deserializing stringified value of type {value.get('class', 'unknown')}. "
                    f"Consider implementing custom serialization for this type."
                )
                return data
            else:
                # Unknown type, return as-is
                return value
        elif isinstance(value, dict):
            # Regular dict without type info
            return {k: self._deserialize_value(v) for k, v in value.items()}
        else:
            # Basic types
            return value


def list_available() -> list[str]:
    """list all available datasets that can be used with @foreach decorator.

    This function provides a convenient way to discover what datasets are
    available in the current environment. The returned dataset names can be
    used with the @foreach decorator using the syntax @foreach.dataset_name().

    Returns:
        list of dataset names sorted alphabetically

    Examples:
        ```python
        >>> from dotevals.datasets import list_available
        >>> datasets = list_available()
        >>> print(datasets)
        ['bfcl', 'gsm8k', 'sroie']

        # Use discovered dataset
        >>> from dotevals import foreach
        >>> @foreach.gsm8k("test")
        ... def evaluate(question, reasoning, answer, model):
        ...     # evaluation logic
        ...     pass
        ```

    See Also:
        get_dataset_info: Get detailed information about a specific dataset
    """
    from dotevals.datasets import registry

    return registry.list_datasets()


def get_dataset_info(name: str) -> dict:
    """Get detailed information about a specific dataset.

    This function retrieves metadata about a dataset without instantiating it.
    Useful for understanding what columns a dataset provides and what splits
    are available before using it in evaluations.

    Args:
        name: The name of the dataset to get information about

    Returns:
        Dictionary containing:
            - name (str): The dataset's name
            - splits (list[str]): Available data splits (empty list if no splits)
            - columns (list[str]): Column names that will be provided
            - num_rows (int | None): Total rows if known, None otherwise

    Raises:
        ValueError: If the dataset name is not found

    Examples:
        ```python
        >>> from dotevals.datasets import get_dataset_info
        >>> info = get_dataset_info("gsm8k")
        >>> print(info)
        {
            'name': 'gsm8k',
            'splits': ['train', 'test'],
            'columns': ['question', 'reasoning', 'answer'],
            'num_rows': None
        }

        # Use this info to understand the dataset structure
        >>> @foreach.gsm8k("test")
        ... def evaluate(question, reasoning, answer, model):
        ...     # We know we'll receive these three columns
        ...     pass
        ```

    See Also:
        list_available: Discover all available datasets
    """
    from dotevals.datasets import registry

    dataset_class = registry.get_dataset_class(name)
    return {
        "name": dataset_class.name,
        "splits": getattr(dataset_class, "splits", []),
        "columns": dataset_class.columns,
        "num_rows": getattr(dataset_class, "num_rows", None),
    }
