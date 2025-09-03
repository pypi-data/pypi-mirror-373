from .base import Storage
from .registry import registry

# Expose commonly used functions for convenience
get_storage = registry.get_storage
list_backends = registry.list_backends
register = registry.register

__all__ = ["Storage", "registry", "get_storage", "list_backends", "register"]
