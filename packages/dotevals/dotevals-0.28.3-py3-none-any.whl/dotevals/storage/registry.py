"""Storage backend registry for dotevals."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import Storage


class StorageRegistry:
    """Registry for storage backends."""

    def __init__(self):
        self._backends = {}
        self._plugins_loaded = False

        # Register built-in backends
        from .json import JSONStorage

        self.register("json", JSONStorage)

    def register(self, name: str, storage_class: type["Storage"]) -> None:
        """Register a storage backend.

        Args:
            name: The name of the backend (e.g., "json", "sqlite", "redis")
            storage_class: The storage class that implements the Storage interface

        """
        self._backends[name] = storage_class

    def get_backend(self, name: str) -> type["Storage"]:
        """Get a storage backend by name.

        Args:
            name: The name of the backend

        Returns:
            The storage class

        Raises:
            ValueError: If the backend is not registered
        """
        if name not in self._backends:
            raise ValueError(f"Unknown storage backend: {name}")
        return self._backends[name]

    def get_storage(self, storage_path: str | None = None) -> "Storage":
        """Get a storage instance based on the storage path.

        The storage path format is: backend://path
        For backward compatibility, paths without a backend default to JSON.

        Args:
            storage_path: The storage path (e.g., "json://data", "sqlite://db.sqlite")
                         If None, defaults to "json://.dotevals"

        Returns:
            A storage instance

        Raises:
            ValueError: If the backend is not registered
        """
        # Ensure plugins are loaded
        self.load_plugins()

        storage_path = "json://.dotevals" if storage_path is None else storage_path

        if "://" in storage_path:
            backend_name, path = storage_path.split("://", 1)
        else:
            backend_name, path = "json", storage_path

        backend_class = self.get_backend(backend_name)

        return backend_class(path)  # type: ignore[call-arg]

    def list_backends(self) -> list[str]:
        """List all registered backend names."""
        # Ensure plugins are loaded
        self.load_plugins()
        return list(self._backends.keys())

    def load_plugins(self, force: bool = False):
        """Load storage backends from entry points.

        Args:
            force: If True, reload plugins even if already loaded
        """
        if self._plugins_loaded and not force:
            return

        try:
            import importlib.metadata

            # Load all entry points in the dotevals.storage group
            entry_points = importlib.metadata.entry_points()

            # Handle different Python versions
            storage_entries = []
            if hasattr(entry_points, "select"):
                # Python 3.10+
                storage_entries = list(entry_points.select(group="dotevals.storage"))
            else:
                # Python 3.9 - entry_points is a dict-like object
                group = entry_points.get("dotevals.storage")
                if group is not None:
                    storage_entries = list(group)

            for entry_point in storage_entries:
                try:
                    # Load the storage class
                    storage_class = entry_point.load()
                    # Register it with the name from entry point
                    self.register(entry_point.name, storage_class)
                except Exception as e:
                    # Log but don't fail if a plugin can't be loaded
                    import warnings

                    warnings.warn(
                        f"Failed to load storage plugin '{entry_point.name}': {e}",
                        RuntimeWarning,
                    )
        except ImportError:
            # importlib.metadata not available (shouldn't happen in Python 3.8+)
            pass

        self._plugins_loaded = True


# Global registry instance
registry = StorageRegistry()
