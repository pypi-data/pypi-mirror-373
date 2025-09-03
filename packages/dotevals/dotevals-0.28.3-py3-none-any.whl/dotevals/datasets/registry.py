"""Registry for dataset plugins."""

import importlib.metadata
import warnings

from .base import Dataset


class DatasetRegistry:
    """Central registry for managing dataset plugins.

    The DatasetRegistry is responsible for discovering, loading, and managing
    dataset plugins. It uses Python's entry points mechanism to dynamically
    discover datasets installed in the Python environment.

    The registry follows a lazy discovery pattern - plugins are only discovered
    when first needed, reducing startup time. Once discovered, dataset classes
    are cached for efficient access.

    Entry points should be registered in the "dotevals.datasets" group.

    Examples:
        In your package's pyproject.toml:

        ```toml
        [project.entry-points."dotevals.datasets"]
        my_dataset = "my_package.datasets:MyDataset"
        ```

    Attributes:
        _dataset_classes: Dictionary mapping dataset names to their classes
        _discovery_completed: Flag indicating whether plugin discovery has been performed.
            This is necessary because an empty _dataset_classes could mean either
            "not discovered yet" or "discovered but no plugins found".
    """

    def __init__(self):
        self._dataset_classes: dict[str, type[Dataset]] = {}  # type: ignore[attr-defined]
        # Track whether discovery has been performed, even if no plugins were found
        self._discovery_completed = False

    def discover_plugins(self, force: bool = False) -> None:
        """Discover and load all installed dataset plugins.

        This method scans for entry points in the "dotevals.datasets" group
        and loads the corresponding dataset classes. Invalid plugins (those
        that don't inherit from Dataset) are skipped with a warning.

        The discovery process is cached - subsequent calls will not re-discover
        unless force=True is specified.

        Args:
            force: If True, force re-discovery even if already performed.
                  Useful for testing or when plugins may have been installed
                  after the initial discovery.

        Note:
            Discovery happens automatically when needed (e.g., when calling
            get_dataset_class or list_datasets), so manual calls to this
            method are typically not necessary.
        """
        if self._discovery_completed and not force:
            return

        # Discover from entry points
        try:
            # Try the new API first (Python 3.10+)
            dataset_entry_points = importlib.metadata.entry_points(
                group="dotevals.datasets"
            )
        except TypeError:
            # Fall back to older API
            entry_points = importlib.metadata.entry_points()
            dataset_entry_points = entry_points.get("dotevals.datasets", [])  # type: ignore[attr-defined, arg-type]

        for entry_point in dataset_entry_points:
            try:
                dataset_class = entry_point.load()

                if not issubclass(dataset_class, Dataset):
                    plugin_name = getattr(entry_point, "name", str(entry_point))
                    warnings.warn(f"Plugin {plugin_name} does not inherit from Dataset")
                    continue

                self.register(dataset_class)

            except Exception as e:
                plugin_name = getattr(entry_point, "name", str(entry_point))
                warnings.warn(f"Failed to load plugin {plugin_name}: {e}")

        self._discovery_completed = True

    def register(self, dataset_class: type[Dataset]):
        """Register a dataset class in the registry.

        This method can be used to manually register dataset classes without
        using the entry points mechanism. This is useful for testing or for
        registering datasets dynamically at runtime.

        The registration is idempotent - registering the same class multiple
        times has no effect. However, attempting to register a different class
        with the same name will raise an error.

        Args:
            dataset_class: A class that inherits from Dataset and has all
                          required attributes (name, splits, columns)

        Raises:
            ValueError: If a different class is already registered with the
                       same name as dataset_class.name
            AttributeError: If dataset_class lacks required attributes
        """
        name = dataset_class.name
        if name in self._dataset_classes:
            # Allow re-registration of the same class (idempotent)
            if self._dataset_classes[name] is dataset_class:
                return
            raise ValueError(
                f"Tried to register {name}, but it was already registered with a different class."
            )
        self._dataset_classes[name] = dataset_class

    def get_dataset_class(self, name: str) -> type[Dataset]:
        """Retrieve a dataset class by its name.

        This method will trigger plugin discovery if it hasn't been performed
        yet. The returned class can be instantiated to create a dataset instance.

        Args:
            name: The name of the dataset (as defined by the Dataset.name attribute)

        Returns:
            The Dataset class corresponding to the given name

        Raises:
            ValueError: If no dataset with the given name is found

        Examples:
            ```python
            >>> dataset_cls = registry.get_dataset_class("gsm8k")
            >>> dataset = dataset_cls(split="test")
            ```
        """
        self.discover_plugins()

        if name not in self._dataset_classes:
            raise ValueError(
                f"Dataset '{name}' not found. "
                f"Available datasets: {self.list_datasets()}"
            )
        return self._dataset_classes[name]

    def list_datasets(self) -> list[str]:
        """list all available dataset names.

        This method will trigger plugin discovery if it hasn't been performed
        yet. The returned names can be used with get_dataset_class() or with
        the @foreach.dataset_name() decorator syntax.

        Returns:
            list of registered dataset names, sorted alphabetically

        Examples:
            ```python
            >>> available = registry.list_datasets()
            >>> print(available)
            ['bfcl', 'gsm8k', 'sroie']
            ```
        """
        self.discover_plugins()
        return list(self._dataset_classes.keys())


# Create singleton instance
registry = DatasetRegistry()
