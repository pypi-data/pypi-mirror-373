"""Executor plugins for different evaluation strategies."""

# Import executors to trigger registration
from . import batch, foreach  # noqa: F401
from .base import Executor
from .registry import executor_registry

__all__ = ["Executor", "executor_registry"]
