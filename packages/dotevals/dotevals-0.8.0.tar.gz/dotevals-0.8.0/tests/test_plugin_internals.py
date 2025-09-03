"""Tests for internal plugin functionality."""

from unittest.mock import AsyncMock, MagicMock, patch

from dotevals.plugin import pytest_configure, pytest_sessionfinish


class MockConfig:
    """Mock pytest config object."""

    def __init__(self):
        self._options = {}
        self._dotevals_items = []
        self._evaluation_results = {}

    def getoption(self, name, default=None):
        return self._options.get(name, default)

    def setoption(self, name, value):
        self._options[name] = value

    def addinivalue_line(self, name, value):
        """Mock addinivalue_line method."""
        pass


class MockSession:
    """Mock pytest session object."""

    def __init__(self, config=None):
        self.config = config if config else MockConfig()


class MockItem:
    """Mock pytest item object."""

    def __init__(self, function, name="test_item"):
        self.function = function
        self.name = name


def test_pytest_configure_basic():
    """Test basic plugin configuration."""
    config = MockConfig()

    pytest_configure(config)

    # Should set up basic configuration
    assert hasattr(config, "_evaluation_results")
    assert hasattr(config, "_dotevals_items")
    assert config._evaluation_results == {}
    assert config._dotevals_items == []


def test_pytest_configure_with_concurrent():
    """Test plugin configuration with concurrent option."""
    config = MockConfig()
    config.setoption("concurrent", True)

    pytest_configure(config)

    # Should still work, concurrent is handled at session finish
    assert hasattr(config, "_evaluation_results")
    assert hasattr(config, "_dotevals_items")


@patch("dotevals.runner.Runner")
def test_pytest_sessionfinish_with_concurrent_items(MockRunner):
    """Test pytest session finish with runner system."""
    # Setup mock
    mock_runner_instance = MagicMock()
    mock_runner_instance.run_evaluations = AsyncMock()
    MockRunner.return_value = mock_runner_instance

    # Create mock config with concurrent enabled
    config = MockConfig()
    config.setoption("concurrent", True)
    config.setoption("--experiment", "test_exp")
    config.setoption("--samples", 10)

    # Create async mock item
    async_func = AsyncMock()
    async_func.__name__ = "test_async"
    mock_item = MockItem(async_func, "test_async")

    config._dotevals_items = [mock_item]

    # Create session
    session = MockSession(config)

    # Run sessionfinish
    pytest_sessionfinish(session, 0)

    # Should have created a runner and run evaluations
    MockRunner.assert_called_once()
    mock_runner_instance.run_evaluations.assert_called_once()


@patch("dotevals.runner.Runner")
def test_pytest_sessionfinish_no_concurrent_items(MockRunner):
    """Test session finish with no concurrent option."""
    # Setup mock
    mock_runner_instance = MagicMock()
    mock_runner_instance.run_evaluations = AsyncMock()
    MockRunner.return_value = mock_runner_instance

    # Create mock config
    config = MockConfig()
    config.setoption("concurrent", False)  # No concurrent

    # Create sync mock item
    sync_func = MagicMock()
    sync_func.__name__ = "test_sync"
    mock_item = MockItem(sync_func, "test_sync")

    config._dotevals_items = [mock_item]

    # Create session
    session = MockSession(config)

    # Run sessionfinish
    pytest_sessionfinish(session, 0)

    # Should have created a runner with concurrent=False
    MockRunner.assert_called_once_with(
        experiment_name=None,
        storage=None,
        samples=None,
        concurrent=False,
        results_dict=config._evaluation_results,
    )


def test_pytest_sessionfinish_no_dotevals_items():
    """Test session finish with no dotevals items."""
    # Create mock config with no items
    config = MockConfig()
    config._dotevals_items = []

    # Create session
    session = MockSession(config)

    # Run sessionfinish - should exit early
    pytest_sessionfinish(session, 0)

    # No runner should be created
    assert config._evaluation_results == {}


@patch("dotevals.runner.Runner")
def test_pytest_sessionfinish_mixed_items(MockRunner):
    """Test session finish with mixed sync/async items."""
    # Setup mock
    mock_runner_instance = MagicMock()
    mock_runner_instance.run_evaluations = AsyncMock()
    MockRunner.return_value = mock_runner_instance

    # Create mock config
    config = MockConfig()
    config.setoption("concurrent", True)

    # Create mixed items
    sync_func = MagicMock()
    sync_func.__name__ = "test_sync"
    sync_item = MockItem(sync_func, "test_sync")

    async_func = AsyncMock()
    async_func.__name__ = "test_async"
    async_item = MockItem(async_func, "test_async")

    config._dotevals_items = [sync_item, async_item]

    # Create session
    session = MockSession(config)

    # Run sessionfinish
    pytest_sessionfinish(session, 0)

    # Should have created a runner and run all evaluations
    MockRunner.assert_called_once()
    mock_runner_instance.run_evaluations.assert_called_once_with(
        [sync_item, async_item]
    )
