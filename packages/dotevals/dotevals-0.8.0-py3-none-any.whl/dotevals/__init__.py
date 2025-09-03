from .decorators import Batch as Batch
from .decorators import ForEach as ForEach
from .decorators import batch as batch
from .decorators import foreach as foreach
from .interactive import run as run
from .results import Result as Result

__all__ = ["Batch", "batch", "ForEach", "foreach", "Result", "run"]


def __getattr__(name: str):
    """Dynamic attribute access for plugin decorators.

    This allows importing plugin decorators directly from dotevals:

        >>> from dotevals import async_batch

    """
    # Try to get it from decorators module
    import dotevals.decorators

    try:
        return getattr(dotevals.decorators, name)
    except AttributeError:
        # Re-raise with better error message
        raise AttributeError(f"module 'dotevals' has no attribute '{name}'")


def __dir__():
    """List available attributes including all plugin decorators.

    This enables tab completion for plugin decorators like async_batch.
    """
    from dotevals.executors.registry import executor_registry

    # Discover and get all executor names (these can be imported as decorators)
    executor_registry.discover_plugins()
    executor_names = list(executor_registry._executors.keys())

    return __all__ + executor_names
