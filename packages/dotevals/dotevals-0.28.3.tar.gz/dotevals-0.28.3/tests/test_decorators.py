"""Parametrized tests for @foreach and @batch decorators."""

import asyncio

import pytest

from dotevals import Batch, ForEach, batch, foreach
from dotevals.decorators import create_dataset_decorator, create_decorator
from dotevals.evaluators import exact_match
from dotevals.results import Result, Score
from dotevals.sessions import SessionManager


@pytest.fixture
def simple_dataset():
    """Basic 3-item dataset for testing."""
    return [("a", 1), ("b", 2), ("c", 3)]


@pytest.fixture
def session_manager(tmp_path):
    """Session manager with JSON storage."""
    import uuid

    unique_id = str(uuid.uuid4())[:8]
    return SessionManager(
        evaluation_name=f"test_eval_{unique_id}",
        experiment_name=f"test_exp_{unique_id}",
        storage=f"json://{tmp_path}/evaluations",
    )


class TestDecoratorFunctionality:
    """Parametrized tests for decorator functionality."""

    @pytest.mark.parametrize(
        "decorator_type,is_async,executor_name",
        [
            (foreach, False, "foreach"),
            (foreach, True, "foreach"),
            (batch, False, "batch"),
            (batch, True, "batch"),
        ],
        ids=["foreach_sync", "foreach_async", "batch_sync", "batch_async"],
    )
    def test_decorator_basic_functionality(
        self, decorator_type, is_async, executor_name, simple_dataset, session_manager
    ):
        """Test basic decorator functionality for sync and async functions."""

        if decorator_type == foreach:
            if is_async:

                @decorator_type("text,number", simple_dataset)
                async def eval_fn(text, number):
                    await asyncio.sleep(0)  # Simulate async work
                    return Result(exact_match(text, text))
            else:

                @decorator_type("text,number", simple_dataset)
                def eval_fn(text, number):
                    return Result(exact_match(text, text))
        else:  # batch
            if is_async:

                @decorator_type("text,number", simple_dataset)
                async def eval_fn(text, number):
                    await asyncio.sleep(0)  # Simulate async work
                    results = []
                    for t, n in zip(text, number):
                        results.append(Result(exact_match(t, t)))
                    return results
            else:

                @decorator_type("text,number", simple_dataset)
                def eval_fn(text, number):
                    results = []
                    for t, n in zip(text, number):
                        results.append(Result(exact_match(t, t)))
                    return results

        # Run evaluation
        if is_async:
            coro = eval_fn(session_manager, samples=None)
            summary = asyncio.run(coro)
        else:
            coro = eval_fn(session_manager, samples=None)
            summary = asyncio.run(coro)

        # Verify results
        assert summary.summary["exact_match"]["accuracy"] == 1.0
        assert len(summary.results) == 3

        # Check executor name
        from dotevals.evaluation import Evaluation

        assert isinstance(eval_fn, Evaluation)
        assert eval_fn.executor_name == executor_name

    @pytest.mark.parametrize(
        "decorator_class,executor_name",
        [
            (ForEach, "foreach"),
            (Batch, "batch"),
        ],
        ids=["ForEach", "Batch"],
    )
    def test_decorator_instance_creation(
        self, decorator_class, executor_name, tmp_path
    ):
        """Test decorator instance creation for ForEach and Batch."""
        import uuid

        decorator_instance = decorator_class()

        if decorator_class == ForEach:

            @decorator_instance("text", [("a",)])
            def eval_fn(text):
                return Result(exact_match(text, "a"))
        else:  # Batch

            @decorator_instance("text", [("a",)])
            def eval_fn(text):
                return [Result(exact_match(t, "a")) for t in text]

        unique_id = str(uuid.uuid4())[:8]
        session_manager = SessionManager(
            experiment_name=f"test_instance_{unique_id}",
            evaluation_name=f"test_eval_{unique_id}",
            storage=f"json://{tmp_path}/evaluations",
        )

        coro = eval_fn(session_manager, samples=None)
        summary = asyncio.run(coro)
        assert summary.summary["exact_match"]["accuracy"] == 1.0

    @pytest.mark.parametrize(
        "decorator_type,dataset_size,column_spec",
        [
            (foreach, 1, "text"),
            (foreach, 5, "text,number"),
            (foreach, 10, "a,b,c"),
            (batch, 1, "text"),
            (batch, 5, "text,number"),
            (batch, 10, "a,b,c"),
        ],
        ids=[
            "foreach_single",
            "foreach_medium",
            "foreach_multi_col",
            "batch_single",
            "batch_medium",
            "batch_multi_col",
        ],
    )
    def test_decorator_dataset_sizes(
        self, decorator_type, dataset_size, column_spec, session_manager
    ):
        """Test decorators with various dataset sizes and column specifications."""
        # Generate dataset based on column_spec
        columns = column_spec.split(",")
        dataset = []
        for i in range(dataset_size):
            row = tuple(f"{col}_{i}" for col in columns)
            dataset.append(row)

        if decorator_type == foreach:

            @decorator_type(column_spec, dataset)
            def eval_fn(*args):
                # Just check we got the right number of arguments
                assert len(args) == len(columns)
                return Result(Score("test", 1.0, [], {}))
        else:  # batch

            @decorator_type(column_spec, dataset)
            def eval_fn(*args):
                # In batch mode, each arg is a list
                assert all(isinstance(arg, list) for arg in args)
                assert all(len(arg) == dataset_size for arg in args)
                return [Result(Score("test", 1.0, [], {})) for _ in range(len(args[0]))]

        coro = eval_fn(session_manager, samples=None)
        summary = asyncio.run(coro)
        assert len(summary.results) == dataset_size

    @pytest.mark.parametrize(
        "decorator_type,kwargs_to_pass",
        [
            (foreach, {"custom_param": "test", "another_param": 42}),
            (foreach, {"flag": True, "threshold": 0.5}),
            (batch, {"custom_param": "batch_test", "flag": False}),
            (batch, {}),  # No extra kwargs
        ],
        ids=["foreach_kwargs1", "foreach_kwargs2", "batch_kwargs", "batch_no_kwargs"],
    )
    def test_decorator_kwargs_passing(
        self, decorator_type, kwargs_to_pass, simple_dataset, session_manager
    ):
        """Test that additional kwargs are passed through correctly."""
        captured_kwargs = []

        if decorator_type == foreach:

            @decorator_type("text,number", simple_dataset)
            def eval_fn(text, number, **kwargs):
                captured_kwargs.append(kwargs)
                return Result(exact_match(text, text))
        else:  # batch

            @decorator_type("text,number", simple_dataset)
            def eval_fn(text, number, **kwargs):
                captured_kwargs.append(kwargs)
                return [Result(exact_match(t, t)) for t in text]

        coro = eval_fn(session_manager, samples=None, **kwargs_to_pass)
        asyncio.run(coro)

        # Verify kwargs were passed
        assert len(captured_kwargs) > 0
        for captured in captured_kwargs:
            for key, value in kwargs_to_pass.items():
                assert captured.get(key) == value


class TestDecoratorEdgeCases:
    """Parametrized tests for decorator edge cases."""

    @pytest.mark.parametrize(
        "decorator_type,dataset",
        [
            (foreach, []),  # Empty dataset
            (batch, []),  # Empty dataset
            (foreach, [("single",)]),  # Single item
            (batch, [("single",)]),  # Single item
        ],
        ids=["foreach_empty", "batch_empty", "foreach_single", "batch_single"],
    )
    def test_decorator_edge_datasets(self, decorator_type, dataset, session_manager):
        """Test decorators with edge case datasets."""
        if decorator_type == foreach:

            @decorator_type("text", dataset)
            def eval_fn(text):
                return Result(Score("test", 1.0, [], {}))
        else:  # batch

            @decorator_type("text", dataset)
            def eval_fn(text):
                return [Result(Score("test", 1.0, [], {})) for _ in text]

        coro = eval_fn(session_manager, samples=None)
        summary = asyncio.run(coro)
        assert len(summary.results) == len(dataset)

    @pytest.mark.parametrize(
        "error_type,error_index",
        [
            (ValueError, 0),  # Error on first item
            (TypeError, 1),  # Error on middle item
            (KeyError, 2),  # Error on last item
        ],
        ids=["error_first", "error_middle", "error_last"],
    )
    def test_foreach_error_handling(
        self, error_type, error_index, simple_dataset, session_manager
    ):
        """Test error handling in foreach decorator."""
        call_count = [0]

        @foreach("text,number", simple_dataset)
        def eval_fn(text, number):
            index = call_count[0]
            call_count[0] += 1
            if index == error_index:
                raise error_type(f"Error at index {index}")
            return Result(exact_match(text, text))

        coro = eval_fn(session_manager, samples=None)
        summary = asyncio.run(coro)

        # Should have processed all items
        assert len(summary.results) == 3
        # One should have an error
        errors = [r for r in summary.results if r.error is not None]
        assert len(errors) == 1
        assert error_type.__name__ in errors[0].error


class TestDecoratorUtilities:
    """Tests for decorator utility functions."""

    def test_foreach_getattr_dataset_access(self):
        """Test ForEach.__getattr__ for dataset access."""
        from dotevals import foreach
        from dotevals.datasets import Dataset, registry

        # Create a mock dataset
        class TestDataset(Dataset):
            columns = ["input", "output"]

            def __init__(self, split=None):
                super().__init__(split)

            def __iter__(self):
                yield {"input": "test", "output": "result"}

        # Mock the registry
        original_get = registry.get_dataset_class

        def mock_get_dataset_class(name):
            if name == "test_dataset":
                return TestDataset
            return original_get(name)

        registry.get_dataset_class = mock_get_dataset_class
        try:
            # Access dataset via attribute syntax
            decorator = foreach.test_dataset
            assert callable(decorator)

            # Use the decorator
            dataset_decorator = decorator()

            @dataset_decorator
            def eval_fn(input, output):
                from dotevals.evaluators import exact_match
                from dotevals.results import Result

                return Result(exact_match(input, output))

            from dotevals.evaluation import Evaluation

            assert isinstance(eval_fn, Evaluation)
            assert eval_fn.executor_name == "foreach"

        finally:
            registry.get_dataset_class = original_get

    def test_batch_getattr_dataset_access(self):
        """Test Batch.__getattr__ for dataset access."""
        from dotevals import batch
        from dotevals.datasets import Dataset, registry

        # Create a mock dataset
        class TestDataset(Dataset):
            columns = ["text"]

            def __init__(self, split=None):
                super().__init__(split)

            def __iter__(self):
                yield {"text": "sample1"}
                yield {"text": "sample2"}

        # Mock the registry
        original_get = registry.get_dataset_class

        def mock_get_dataset_class(name):
            if name == "test_dataset":
                return TestDataset
            return original_get(name)

        registry.get_dataset_class = mock_get_dataset_class
        try:
            # Access dataset via attribute syntax
            decorator = batch.test_dataset
            assert callable(decorator)

            # Use the decorator with batch_size
            dataset_decorator = decorator(batch_size=2)

            @dataset_decorator
            def eval_fn(text):
                from dotevals.results import Result, Score

                return [Result(Score("test", 1.0, [], {})) for _ in text]

            from dotevals.evaluation import Evaluation

            assert isinstance(eval_fn, Evaluation)
            assert eval_fn.executor_name == "batch"
            assert eval_fn.executor_kwargs.get("batch_size") == 2

        finally:
            registry.get_dataset_class = original_get

    def test_foreach_getattr_special_methods(self):
        """Test that ForEach.__getattr__ properly handles special methods."""
        from dotevals import foreach

        # Special methods should raise AttributeError
        with pytest.raises(
            AttributeError, match="'ForEach' object has no attribute '__special__'"
        ):
            foreach.__special__

    def test_batch_getattr_special_methods(self):
        """Test that Batch.__getattr__ properly handles special methods."""
        from dotevals import batch

        # Special methods should raise AttributeError
        with pytest.raises(
            AttributeError, match="'Batch' object has no attribute '__special__'"
        ):
            batch.__special__

    @pytest.mark.parametrize(
        "columns,expected_names",
        [
            ("text", ["text"]),
            ("text,number", ["text", "number"]),
            ("a, b, c", ["a", "b", "c"]),  # With spaces
            ("col1,col2,col3,col4", ["col1", "col2", "col3", "col4"]),
        ],
        ids=["single", "double", "spaces", "multiple"],
    )
    def test_column_spec_parsing(self, columns, expected_names):
        """Test column specification parsing."""

        @foreach(columns, [])
        def eval_fn(*args):
            return Result(Score("test", 1.0, [], {}))

        from dotevals.evaluation import Evaluation

        assert isinstance(eval_fn, Evaluation)
        assert eval_fn.column_names == expected_names

    def test_create_decorator_function(self):
        """Test create_decorator utility function."""
        # create_decorator creates decorated functions, not decorator instances
        decorator_fn = create_decorator("foreach", "text", [("a",)])
        assert callable(decorator_fn)

        decorator_fn = create_decorator("batch", "text", [("a",)])
        assert callable(decorator_fn)

    def test_create_dataset_decorator_function(self):
        """Test create_dataset_decorator utility function."""
        from dotevals.datasets import Dataset, registry

        # Create a mock dataset class
        class MockDataset(Dataset):
            columns = ["text", "label"]

            def __init__(self, split=None, **kwargs):
                super().__init__(split)
                self.kwargs = kwargs

            def __iter__(self):
                yield {"text": "test1", "label": "a"}
                yield {"text": "test2", "label": "b"}

        # Mock the registry to return our dataset
        original_get = registry.get_dataset_class

        def mock_get_dataset_class(name):
            if name == "mock_dataset":
                return MockDataset
            return original_get(name)

        registry.get_dataset_class = mock_get_dataset_class
        try:
            # Test creating a dataset decorator
            decorator = create_dataset_decorator("foreach", "mock_dataset")
            assert callable(decorator)

            # Test using the decorator with split
            dataset_decorator = decorator(split="train", custom_param="value")
            assert callable(dataset_decorator)

            # Apply to a function
            @dataset_decorator
            def eval_fn(text, label):
                from dotevals.results import Result, Score

                return Result(Score("test", 1.0, [], {}))

            from dotevals.evaluation import Evaluation

            assert isinstance(eval_fn, Evaluation)
            assert eval_fn.column_spec == "text,label"
            assert eval_fn.executor_name == "foreach"

            # Test with batch and batch_size
            batch_decorator = create_dataset_decorator("batch", "mock_dataset")
            batch_dataset_decorator = batch_decorator(batch_size=2)

            @batch_dataset_decorator
            def batch_eval_fn(text, label):
                from dotevals.results import Result, Score

                return [Result(Score("test", 1.0, [], {})) for _ in text]

            assert isinstance(batch_eval_fn, Evaluation)
            assert batch_eval_fn.executor_kwargs.get("batch_size") == 2

            # Test without split
            no_split_decorator = decorator(custom_key="custom_value")
            assert callable(no_split_decorator)

        finally:
            registry.get_dataset_class = original_get

    def test_decorators_getattr_plugin_import(self, monkeypatch):
        """Test __getattr__ for plugin decorator imports."""
        from unittest.mock import MagicMock

        from dotevals import decorators
        from dotevals.executors.base import Executor
        from dotevals.executors.registry import executor_registry

        # Create a mock executor
        class MockExecutor(Executor):
            @property
            def name(self):
                return "custom_executor"

            def _execute_sync(self, eval_fn, dataset, column_names, samples, **kwargs):
                pass

            async def _execute_async(
                self, eval_fn, dataset, column_names, samples, **kwargs
            ):
                pass

            def execute(self, eval_fn, dataset, column_names, samples, **kwargs):
                pass

        # Register the executor
        mock_executor = MockExecutor()
        original_get = executor_registry.get

        def mock_registry_get(name):
            if name == "custom_executor":
                return mock_executor
            return original_get(name)

        # Mock the plugin package
        mock_package = MagicMock()
        mock_package.custom_executor = "mock_decorator"

        # Mock importlib to return our package
        def mock_import(package_name):
            if package_name == "dotevals_custom_executor":
                return mock_package
            raise ImportError(f"No module named '{package_name}'")

        monkeypatch.setattr(executor_registry, "get", mock_registry_get)
        monkeypatch.setattr("importlib.import_module", mock_import)

        try:
            # Test successful import
            decorator = decorators.__getattr__("custom_executor")
            assert decorator == "mock_decorator"
        finally:
            executor_registry.get = original_get

    def test_decorators_getattr_plugin_missing_decorator(self, monkeypatch):
        """Test __getattr__ when plugin doesn't export decorator."""
        from unittest.mock import MagicMock

        from dotevals import decorators
        from dotevals.executors.base import Executor
        from dotevals.executors.registry import executor_registry

        # Create and register executor
        class MockExecutor(Executor):
            @property
            def name(self):
                return "missing_decorator"

            def _execute_sync(self, eval_fn, dataset, column_names, samples, **kwargs):
                pass

            async def _execute_async(
                self, eval_fn, dataset, column_names, samples, **kwargs
            ):
                pass

            def execute(self, eval_fn, dataset, column_names, samples, **kwargs):
                pass

        mock_executor = MockExecutor()
        original_get = executor_registry.get

        def mock_registry_get(name):
            if name == "missing_decorator":
                return mock_executor
            return original_get(name)

        # Mock package without the decorator
        mock_package = MagicMock()
        del (
            mock_package.missing_decorator
        )  # Package exists but doesn't have the decorator

        def mock_import(package_name):
            if package_name == "dotevals_missing_decorator":
                return mock_package
            raise ImportError(f"No module named '{package_name}'")

        monkeypatch.setattr(executor_registry, "get", mock_registry_get)
        monkeypatch.setattr("importlib.import_module", mock_import)

        try:
            # Should raise AttributeError with specific message
            with pytest.raises(
                AttributeError, match="does not provide a 'missing_decorator' decorator"
            ):
                decorators.__getattr__("missing_decorator")
        finally:
            executor_registry.get = original_get

    def test_decorators_getattr_plugin_import_error(self, monkeypatch):
        """Test __getattr__ when plugin package cannot be imported."""
        from dotevals import decorators
        from dotevals.executors.base import Executor
        from dotevals.executors.registry import executor_registry

        # Create and register executor
        class MockExecutor(Executor):
            @property
            def name(self):
                return "unimportable"

            def _execute_sync(self, eval_fn, dataset, column_names, samples, **kwargs):
                pass

            async def _execute_async(
                self, eval_fn, dataset, column_names, samples, **kwargs
            ):
                pass

            def execute(self, eval_fn, dataset, column_names, samples, **kwargs):
                pass

        mock_executor = MockExecutor()
        original_get = executor_registry.get

        def mock_registry_get(name):
            if name == "unimportable":
                return mock_executor
            return original_get(name)

        # Mock import to always fail
        def mock_import(package_name):
            raise ImportError(f"No module named '{package_name}'")

        monkeypatch.setattr(executor_registry, "get", mock_registry_get)
        monkeypatch.setattr("importlib.import_module", mock_import)

        try:
            # Should raise AttributeError with import error message
            with pytest.raises(AttributeError, match="could not import decorator"):
                decorators.__getattr__("unimportable")
        finally:
            executor_registry.get = original_get

    def test_decorators_getattr_nonexistent_executor(self):
        """Test __getattr__ for non-existent executor."""
        from dotevals import decorators

        # Should raise AttributeError for non-existent attribute
        with pytest.raises(
            AttributeError,
            match="module 'dotevals.decorators' has no attribute 'nonexistent'",
        ):
            decorators.__getattr__("nonexistent")


@pytest.mark.parametrize(
    "decorator_type,execution_mode",
    [
        (foreach, "sequential"),
        (batch, "sequential"),
        (foreach, "concurrent"),
        (batch, "concurrent"),
    ],
    ids=["foreach_seq", "batch_seq", "foreach_con", "batch_con"],
)
def test_decorator_execution_modes(decorator_type, execution_mode, tmp_path):
    """Test decorators in different execution modes."""
    import time
    import uuid

    dataset = [(f"item_{i}", i) for i in range(3)]

    if decorator_type == foreach:

        @decorator_type("text,number", dataset)
        def eval_fn(text, number):
            time.sleep(0.01)  # Simulate work
            return Result(Score("test", float(number), [], {}))
    else:  # batch

        @decorator_type("text,number", dataset)
        def eval_fn(text, number):
            time.sleep(0.01)  # Simulate work
            return [Result(Score("test", float(n), [], {})) for n in number]

    unique_id = str(uuid.uuid4())[:8]
    session_manager = SessionManager(
        experiment_name=f"test_{execution_mode}_{unique_id}",
        evaluation_name=f"eval_{unique_id}",
        storage=f"json://{tmp_path}/evaluations",
    )

    start_time = time.time()
    coro = eval_fn(session_manager, samples=None)
    summary = asyncio.run(coro)
    elapsed = time.time() - start_time

    assert len(summary.results) == 3
    # Basic timing check (not strict due to system variability)
    if execution_mode == "concurrent" and decorator_type == foreach:
        # Concurrent should be faster than sequential for foreach
        assert elapsed < 0.1  # Should take less than 100ms if concurrent
    # For batch, it's always one call so timing is similar


class TestMainPackageDynamicImports:
    """Tests for main package's dynamic import functionality."""

    def test_main_package_getattr_standard_attributes(self):
        """Test that standard exports are accessible via __getattr__."""
        import dotevals

        # Standard exports from __all__
        assert callable(getattr(dotevals, "Batch"))
        assert callable(getattr(dotevals, "batch"))
        assert callable(getattr(dotevals, "ForEach"))
        assert callable(getattr(dotevals, "foreach"))
        assert callable(getattr(dotevals, "run"))
        assert hasattr(dotevals, "Result")

    def test_main_package_getattr_plugin_decorators(self, monkeypatch):
        """Test __getattr__ imports plugin decorators dynamically."""
        from unittest.mock import MagicMock

        import dotevals
        import dotevals.decorators

        # First, mock the decorator in the decorators module's __getattr__
        mock_decorator = MagicMock()
        original_getattr = dotevals.decorators.__getattr__

        def mock_getattr(name):
            if name == "async_batch":
                return mock_decorator
            return original_getattr(name)

        monkeypatch.setattr(dotevals.decorators, "__getattr__", mock_getattr)

        # Access via main package
        decorator = getattr(dotevals, "async_batch")
        assert decorator is mock_decorator

    def test_main_package_getattr_nonexistent(self):
        """Test __getattr__ raises AttributeError for non-existent attributes."""
        import dotevals

        with pytest.raises(
            AttributeError, match="module 'dotevals' has no attribute 'nonexistent'"
        ):
            getattr(dotevals, "nonexistent")

    def test_main_package_dir(self, monkeypatch):
        """Test __dir__ includes plugin decorators."""
        import dotevals
        from dotevals.executors.registry import executor_registry

        # Mock the registry to have some executors
        original_executors = executor_registry._executors.copy()
        executor_registry._executors = {
            "foreach": None,
            "batch": None,
            "async_batch": None,
            "custom_executor": None,
        }

        try:
            dir_contents = dir(dotevals)

            # Check standard exports are included
            assert "Batch" in dir_contents
            assert "batch" in dir_contents
            assert "ForEach" in dir_contents
            assert "foreach" in dir_contents
            assert "Result" in dir_contents
            assert "run" in dir_contents

            # Check plugin executors are included
            assert "async_batch" in dir_contents
            assert "custom_executor" in dir_contents
        finally:
            executor_registry._executors = original_executors

    def test_main_package_dir_with_plugin_discovery(self, monkeypatch):
        """Test __dir__ triggers plugin discovery."""
        from unittest.mock import MagicMock

        import dotevals
        from dotevals.executors.registry import executor_registry

        # Mock discover_plugins
        mock_discover = MagicMock()
        monkeypatch.setattr(executor_registry, "discover_plugins", mock_discover)

        # Call dir() which should trigger discovery
        dir(dotevals)

        # Verify discover_plugins was called
        mock_discover.assert_called_once()
