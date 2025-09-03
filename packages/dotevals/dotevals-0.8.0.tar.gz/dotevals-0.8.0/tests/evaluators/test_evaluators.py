"""Consolidated evaluator tests - more concise with parameterized testing."""

import pytest

from dotevals.evaluators import evaluator, exact_match, numeric_match, valid_json
from dotevals.evaluators.ast_evaluation import ast_evaluation
from dotevals.evaluators.registry import EvaluatorRegistry
from dotevals.metrics import accuracy
from dotevals.results import Score


class TestExactMatch:
    """Tests for exact_match evaluator."""

    @pytest.mark.parametrize(
        "answer,expected,result",
        [
            ("1", "1", True),
            ("1", "2", False),
            ("hello", "hello", True),
            ("Hello", "hello", False),
            (1, 1, True),
            (1, 2, False),
            (None, None, True),
            (None, "", False),
        ],
    )
    def test_exact_match_basic(self, answer, expected, result):
        """Test basic exact match comparisons."""
        score = exact_match(answer, expected)
        assert isinstance(score, Score)
        assert score.value is result
        assert score.name == "exact_match"
        assert len(score.metrics) == 1
        assert score.metrics[0].__name__ == "accuracy"

    @pytest.mark.parametrize("custom_name", ["custom_comparison", "my_evaluator", None])
    def test_exact_match_custom_name(self, custom_name):
        """Test custom naming for exact_match."""
        score = exact_match("test", "test", name=custom_name)
        expected_name = custom_name if custom_name else "exact_match"
        assert score.name == expected_name


class TestNumericMatch:
    """Tests for numeric_match evaluator."""

    @pytest.mark.parametrize(
        "answer,expected,should_match",
        [
            # Basic integers
            (42, 42, True),
            (42, 43, False),
            ("42", "42", True),
            ("42", 42, True),
            (42, "42", True),
            # Floats
            (3.14, 3.14, True),
            ("3.14", 3.14, True),
            (3.14, "3.14", True),
            (3.14, 3.15, False),
            # Numbers with commas
            ("1,234", "1234", True),
            ("1,234,567", "1234567", True),
            ("1,234.56", "1234.56", True),
            # Numbers with spaces
            ("1 234", "1234", True),
            ("1 234 567", "1234567", True),
            ("1 234.56", "1234.56", True),
            # Scientific notation
            ("1.23e3", "1230", True),
            ("1.23E3", "1230", True),
            ("1.23e-3", "0.00123", True),
            # Special cases
            ("0", 0, True),
            ("-42", -42, True),
            ("", "", False),
            ("abc", "123", False),
            ("12.00", "12", True),
            ("1.0", "1", True),
            # Leading/trailing spaces
            ("  42  ", "42", True),
            ("\t100\n", "100", True),
            # None values (edge cases)
            (None, "42", False),
            ("42", None, False),
            (None, None, False),
            # Space after minus sign (invalid number format)
            ("- 42", "42", False),
            ("- 42", "- 42", False),
        ],
    )
    def test_numeric_match_formats(self, answer, expected, should_match):
        """Test various numeric formats and comparisons."""
        score = numeric_match(answer, expected)
        assert score.value is should_match
        assert score.name == "numeric_match"

    def test_numeric_match_custom_name(self):
        """Test custom naming for numeric_match."""
        score = numeric_match(42, 42, name="number_check")
        assert score.name == "number_check"


class TestValidJson:
    """Tests for valid_json evaluator."""

    @pytest.mark.parametrize(
        "text,is_valid",
        [
            # Valid JSON
            ('{"key": "value"}', True),
            ("[]", True),
            ("null", True),
            ("true", True),
            ("false", True),
            ("42", True),
            ('"string"', True),
            ('{"nested": {"key": "value"}}', True),
            ("[1, 2, 3]", True),
            # Invalid JSON
            ("", False),
            ("{", False),
            ('{"key": }', False),
            ("{'key': 'value'}", False),  # Single quotes
            ("undefined", False),
            ('{key: "value"}', False),  # Unquoted key
            ('{"key": "value",}', False),  # Trailing comma
            # Special cases
            ('  {"key": "value"}  ', True),  # With whitespace
            ('{"unicode": "🎉"}', True),  # Unicode
        ],
    )
    def test_valid_json_basic(self, text, is_valid):
        """Test JSON validation."""
        score = valid_json(text)
        assert score.value is is_valid
        assert score.name == "valid_json"

    def test_valid_json_custom_name(self):
        """Test custom naming for valid_json."""
        score = valid_json('{"valid": true}', name="json_check")
        assert score.name == "json_check"

    def test_valid_json_with_schema(self):
        """Test valid_json with JSON schema validation."""
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}, "age": {"type": "number"}},
            "required": ["name"],
        }

        # Valid JSON matching schema
        score = valid_json('{"name": "Alice", "age": 30}', schema=schema)
        assert score.value is True

        # Valid JSON not matching schema (missing required field)
        score = valid_json('{"age": 30}', schema=schema)
        assert score.value is False

        # Invalid schema
        score = valid_json('{"name": "Alice"}', schema={"type": "invalid_type"})
        assert score.value is False

    def test_valid_json_none_input(self):
        """Test valid_json with None input."""
        # Test None value
        score = valid_json(None)
        assert score.value is False


class TestAstEvaluation:
    """Tests for ast_evaluation evaluator with function call schema matching."""

    def test_ast_evaluation_exact_match(self):
        """Test exact function call matching."""
        result = {"calculate": {"x": 5, "y": 3}}
        expected = [{"calculate": {"x": 5, "y": 3}}]
        schema = [
            {
                "name": "calculate",
                "parameters": {
                    "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}},
                    "required": ["x", "y"],
                },
            }
        ]
        score = ast_evaluation(result, expected, schema)
        assert score.value is True
        assert score.name == "ast_evaluation"

    def test_ast_evaluation_wrong_function(self):
        """Test mismatch when function name is wrong."""
        result = {"wrong": {"x": 5, "y": 3}}
        expected = [{"calculate": {"x": 5, "y": 3}}]
        schema = [
            {
                "name": "calculate",
                "parameters": {
                    "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}},
                    "required": ["x", "y"],
                },
            }
        ]
        score = ast_evaluation(result, expected, schema)
        assert score.value is False

    def test_ast_evaluation_missing_parameter(self):
        """Test mismatch when required parameter is missing."""
        result = {"calculate": {"x": 5}}
        expected = [{"calculate": {"x": 5, "y": 3}}]
        schema = [
            {
                "name": "calculate",
                "parameters": {
                    "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}},
                    "required": ["x", "y"],
                },
            }
        ]
        score = ast_evaluation(result, expected, schema)
        assert score.value is False

    def test_ast_evaluation_string_normalization(self):
        """Test string normalization in comparisons."""
        result = {"greet": {"name": "Alice", "msg": "HELLO"}}
        expected = [{"greet": {"name": "alice", "msg": "hello"}}]
        schema = [
            {
                "name": "greet",
                "parameters": {
                    "properties": {
                        "name": {"type": "string"},
                        "msg": {"type": "string"},
                    },
                    "required": ["name", "msg"],
                },
            }
        ]
        score = ast_evaluation(result, expected, schema)
        assert score.value is True

    def test_ast_evaluation_set_alternatives(self):
        """Test matching against set of alternatives."""
        result = {"choose": {"color": "red"}}
        expected = [{"choose": {"color": {"red", "blue", "green"}}}]
        schema = [
            {
                "name": "choose",
                "parameters": {
                    "properties": {"color": {"type": "string"}},
                    "required": ["color"],
                },
            }
        ]
        score = ast_evaluation(result, expected, schema)
        assert score.value is True

        # Test non-matching alternative
        result = {"choose": {"color": "yellow"}}
        score = ast_evaluation(result, expected, schema)
        assert score.value is False

    def test_ast_evaluation_optional_param(self):
        """Test optional parameters."""
        result = {"greet": {"name": "Alice"}}
        expected = [{"greet": {"name": "Alice", "greeting": ""}}]
        schema = [
            {
                "name": "greet",
                "parameters": {
                    "properties": {
                        "name": {"type": "string"},
                        "greeting": {"type": "string"},
                    },
                    "required": ["name"],
                },
            }
        ]
        score = ast_evaluation(result, expected, schema)
        assert score.value is True

    def test_ast_evaluation_helper_functions(self):
        """Test helper functions for ast_evaluation."""
        from dotevals.evaluators.ast_evaluation import (
            compare_param_value,
            is_dict_match,
            recursive_normalize,
        )

        # Test recursive_normalize
        assert recursive_normalize("Hello") == "hello"
        assert recursive_normalize(["A", "B"]) == ["a", "b"]
        assert recursive_normalize({"key": "VALUE"}) == {"key": "value"}
        assert recursive_normalize(42) == 42

        # Test is_dict_match
        assert is_dict_match({"a": 1}, {"a": 1}) is True
        assert is_dict_match({"a": 1}, {"a": 2}) is False
        assert is_dict_match({"a": 1, "b": 2}, {"a": 1}) is False

        # Test compare_param_value
        assert compare_param_value("test", "test") is True
        assert compare_param_value("TEST", "test") is True  # normalized
        assert compare_param_value("red", {"red", "blue"}) is True
        assert compare_param_value("green", {"red", "blue"}) is False

        # Test edge cases for is_dict_match
        assert is_dict_match({"a": 1}, [{"a": 1}]) is True  # list of expected
        assert is_dict_match({"a": 1}, "") is True  # empty string expected returns True
        assert is_dict_match({"a": 1}, [""]) is True  # all empty strings

        # Test edge case for compare_param_value
        assert (
            compare_param_value({"key": "val"}, {"key": "val"}) is True
        )  # dict comparison

    def test_ast_evaluation_json_serialization_error(self):
        """Test when model output contains non-serializable objects ."""

        # Create a non-serializable object
        class NonSerializable:
            pass

        result = {"func": {"param": NonSerializable()}}
        expected = [{"func": {"param": "value"}}]
        schema = [
            {
                "name": "func",
                "parameters": {
                    "properties": {"param": {"type": "string"}},
                    "required": ["param"],
                },
            }
        ]
        score = ast_evaluation(result, expected, schema)
        assert score.value is False  # Should fail due to JSON serialization error

    def test_ast_evaluation_missing_expected_param(self):
        """Test when expected param is missing in model output."""
        result = {"greet": {"name": "Alice"}}
        expected = [{"greet": {"name": "Alice", "age": 30}}]  # age is required
        schema = [
            {
                "name": "greet",
                "parameters": {
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "number"},
                    },
                    "required": ["name", "age"],
                },
            }
        ]
        score = ast_evaluation(result, expected, schema)
        assert score.value is False  # Should fail due to missing age param


class TestEvaluatorDecorator:
    """Tests for the @evaluator decorator."""

    def test_evaluator_basic(self):
        """Test basic evaluator decorator usage."""

        @evaluator(metrics=accuracy())
        def custom_eval(answer, expected):
            return answer == expected

        score = custom_eval("test", "test")
        assert isinstance(score, Score)
        assert score.value is True
        assert score.name == "custom_eval"
        assert len(score.metrics) == 1

    def test_evaluator_multiple_metrics(self):
        """Test evaluator with multiple metrics."""
        from dotevals.metrics import metric

        @metric
        def always_one():
            def metric_fn(scores):
                return 1.0

            return metric_fn

        @evaluator(metrics=[accuracy(), always_one()])
        def multi_metric_eval(a, b):
            return a == b

        score = multi_metric_eval(1, 1)
        assert len(score.metrics) == 2
        assert score.metrics[0].__name__ == "accuracy"
        assert score.metrics[1].__name__ == "always_one"

    def test_evaluator_with_metadata(self):
        """Test that evaluator captures metadata."""

        @evaluator(metrics=accuracy())
        def eval_with_metadata(answer, expected, threshold=0.5):
            return answer >= threshold

        score = eval_with_metadata(0.7, None, threshold=0.6)
        assert score.metadata == {"answer": 0.7, "expected": None, "threshold": 0.6}

    def test_evaluator_custom_name_override(self):
        """Test that custom name overrides function name."""

        @evaluator(metrics=accuracy())
        def my_evaluator(a, b):
            return a == b

        score = my_evaluator(1, 1, name="custom_name")
        assert score.name == "custom_name"


class TestEvaluatorRegistry:
    """Tests for the evaluator registry."""

    def test_registry_has_builtin_evaluators(self):
        """Test registry auto-discovers built-in evaluators."""
        registry = EvaluatorRegistry()
        evaluators = registry.list_evaluators()

        # Should have built-in evaluators
        assert "exact_match" in evaluators
        assert "numeric_match" in evaluators
        assert "valid_json" in evaluators
        assert "ast_evaluation" in evaluators

    def test_registry_registration(self):
        """Test registering custom evaluators."""
        registry = EvaluatorRegistry()
        initial_count = len(registry.list_evaluators())

        def dummy_evaluator():
            return Score("dummy", True, [])

        registry.register("dummy", dummy_evaluator)
        assert "dummy" in registry.list_evaluators()
        assert registry.get("dummy") == dummy_evaluator
        assert len(registry.list_evaluators()) == initial_count + 1

    def test_registry_get_builtin(self):
        """Test getting built-in evaluators."""
        registry = EvaluatorRegistry()

        # Should be able to get built-in evaluators
        assert registry.get("exact_match") is not None
        assert registry.get("numeric_match") is not None
        assert registry.get("valid_json") is not None

    def test_registry_get_nonexistent(self):
        """Test getting non-existent evaluator returns None."""
        registry = EvaluatorRegistry()
        assert registry.get("nonexistent") is None

    def test_registry_duplicate_registration(self):
        """Test that duplicate registration overwrites."""
        registry = EvaluatorRegistry()

        def evaluator1():
            return Score("eval1", True, [])

        def evaluator2():
            return Score("eval2", False, [])

        registry.register("test_dup", evaluator1)
        assert registry.get("test_dup") == evaluator1

        registry.register("test_dup", evaluator2)
        assert registry.get("test_dup") == evaluator2

    def test_registry_discover_plugins(self):
        """Test plugin discovery mechanism."""
        registry = EvaluatorRegistry()
        initial_evaluators = registry.list_evaluators()

        # Registry auto-discovers on init, so should have evaluators
        assert len(initial_evaluators) > 0
        assert "exact_match" in initial_evaluators
        assert "numeric_match" in initial_evaluators

    def test_registry_methods_exist(self):
        """Test that registry has expected methods."""
        registry = EvaluatorRegistry()
        # Check core methods exist
        assert hasattr(registry, "register")
        assert hasattr(registry, "get")
        assert hasattr(registry, "list_evaluators")
        # Registry should have evaluators already discovered
        assert len(registry.list_evaluators()) > 0


def test_evaluator_registry_plugin_loading():
    """Test evaluator registry plugin loading."""
    from unittest.mock import MagicMock, patch

    from dotevals.evaluators.registry import EvaluatorRegistry

    registry = EvaluatorRegistry()

    # Mock entry points
    mock_entry_point = MagicMock()
    mock_entry_point.name = "plugin_evaluator"
    mock_entry_point.load.return_value = lambda x: x  # Simple evaluator

    with patch("importlib.metadata.entry_points") as mock_entry_points:
        mock_entry_points.return_value = {"dotevals.evaluators": [mock_entry_point]}

        # Load plugins
        registry.load_plugins()

        # Check plugin was loaded
        assert "plugin_evaluator" in registry.list_evaluators()
        assert registry.get("plugin_evaluator") is not None


def test_evaluator_registry_plugin_error():
    """Test evaluator registry handles plugin errors."""
    from unittest.mock import MagicMock, patch

    from dotevals.evaluators.registry import EvaluatorRegistry

    registry = EvaluatorRegistry()

    # Mock entry points that fail to load
    mock_entry_point = MagicMock()
    mock_entry_point.name = "bad_plugin"
    mock_entry_point.load.side_effect = ImportError("Plugin failed")

    with patch("importlib.metadata.entry_points") as mock_entry_points:
        mock_entry_points.return_value = {"dotevals.evaluators": [mock_entry_point]}

        # Should handle error gracefully
        registry.load_plugins()

        # Bad plugin should not be loaded
        assert "bad_plugin" not in registry.list_evaluators()


def test_evaluator_module_imports():
    """Test dynamic imports from evaluators module."""
    # Test __getattr__ for successful import
    from dotevals import evaluators

    em = evaluators.exact_match
    assert em is not None

    # Test __dir__ listing
    available = dir(evaluators)
    assert "exact_match" in available
    assert "numeric_match" in available

    # Test AttributeError for non-existent evaluator
    import pytest

    with pytest.raises(AttributeError, match="No evaluator named 'nonexistent'"):
        _ = evaluators.nonexistent


def test_additional_evaluator():
    # Test more numeric_match edge cases
    score = numeric_match(float("inf"), float("inf"))
    assert score.value is True

    score = numeric_match(float("nan"), float("nan"))
    assert score.value is False

    # Test exact_match with custom types
    class CustomObj:
        def __eq__(self, other):
            return True

    obj = CustomObj()
    score = exact_match(obj, "anything")
    assert score.value is True


def test_ast_evaluation_edge_cases():
    """Test ast_evaluation edge cases"""
    from dotevals.evaluators.ast_evaluation import (
        ast_evaluation,
        compare_param_value,
        recursive_normalize,
    )

    # Test list normalization in recursive_normalize
    assert recursive_normalize({"items": ["A", "B"]}) == {"items": ["a", "b"]}
    assert recursive_normalize({"nested": {"key": "VALUE"}}) == {
        "nested": {"key": "value"}
    }
    assert recursive_normalize(42) == 42  # Numbers unchanged
    assert recursive_normalize(None) is None  # None unchanged

    # Test compare_param_value with list expected values
    assert compare_param_value({"a": 1}, [{"a": 1}, {"b": 2}]) is True
    assert compare_param_value({"c": 3}, [{"a": 1}, {"b": 2}]) is False

    # Test with empty result (no function call)
    result = {}
    expected = [{"func": {}}]
    schema = [{"name": "func", "parameters": {}}]
    score = ast_evaluation(result, expected, schema)
    assert score.value is False

    # Test with extra parameters (should fail)
    result = {"calculate": {"x": 5, "y": 3, "z": 1}}
    expected = [{"calculate": {"x": 5, "y": 3}}]
    schema = [
        {
            "name": "calculate",
            "parameters": {
                "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}},
                "required": ["x", "y"],
            },
        }
    ]
    score = ast_evaluation(result, expected, schema)
    assert score.value is False


def test_registry_plugin_loading():
    """Test registry plugin loading mechanisms."""
    from unittest.mock import Mock, patch

    from dotevals.evaluators.registry import EvaluatorRegistry
    from dotevals.results import Score

    # Test with mock entry points
    mock_entry_point = Mock()
    mock_entry_point.name = "test_evaluator"

    def test_eval_func():
        return Score("test", True, [])

    mock_entry_point.load.return_value = test_eval_func

    with patch("importlib.metadata.entry_points") as mock_eps:
        # Mock entry_points to return our test evaluator
        mock_group = Mock()
        mock_group.select.return_value = [mock_entry_point]
        mock_eps.return_value = mock_group

        registry = EvaluatorRegistry()
        # Since registry auto-discovers, test_evaluator should be there
        # Or manually discover to ensure it's loaded
        evaluators = registry.list_evaluators()
        # Just verify the registry works with mocked entry points
        assert isinstance(evaluators, list)


def test_evaluator_basic_integration():
    """Basic integration test for key evaluators."""
    # Test exact_match
    score = exact_match("hello", "hello")
    assert score.value is True
    assert score.name == "exact_match"

    # Test numeric_match
    score = numeric_match("1,234.56", 1234.56)
    assert score.value is True
    assert score.name == "numeric_match"

    # Test valid_json
    score = valid_json('{"valid": true}')
    assert score.value is True
    assert score.name == "valid_json"

    # Test ast_evaluation with proper schema
    from dotevals.evaluators.ast_evaluation import ast_evaluation as ast_eval_func

    result = {"calculate": {"x": 5, "y": 3}}
    expected = [{"calculate": {"x": 5, "y": 3}}]
    schema = [
        {
            "name": "calculate",
            "parameters": {
                "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}},
                "required": ["x", "y"],
            },
        }
    ]
    score = ast_eval_func(result, expected, schema)
    assert score.value is True
    assert score.name == "ast_evaluation"


class TestEvaluatorsDynamicImports:
    """Tests for evaluators module's dynamic import functionality."""

    def test_evaluators_getattr_builtin_evaluators(self):
        """Test __getattr__ for built-in evaluators."""
        from dotevals import evaluators

        # Test accessing built-in evaluators
        em = getattr(evaluators, "exact_match")
        assert callable(em)

        nm = getattr(evaluators, "numeric_match")
        assert callable(nm)

        vj = getattr(evaluators, "valid_json")
        assert callable(vj)

        # Verify they are the actual evaluators
        score = em("test", "test")
        assert score.name == "exact_match"
        assert score.value is True

    def test_evaluators_getattr_nonexistent(self):
        """Test __getattr__ raises AttributeError for non-existent evaluators."""
        from dotevals import evaluators

        with pytest.raises(AttributeError) as exc_info:
            getattr(evaluators, "nonexistent_evaluator")

        error_msg = str(exc_info.value)
        assert "No evaluator named 'nonexistent_evaluator'" in error_msg
        assert "Available evaluators:" in error_msg
        # Check some known evaluators are listed
        assert "exact_match" in error_msg
        assert "numeric_match" in error_msg

    def test_evaluators_getattr_plugin_evaluator(self, monkeypatch):
        """Test __getattr__ for plugin evaluators."""
        from unittest.mock import MagicMock

        from dotevals import evaluators
        from dotevals.evaluators.registry import registry

        # Create a mock evaluator
        mock_evaluator = MagicMock()
        mock_evaluator.return_value = Score("custom", True, [], {})

        # Mock the registry to return our evaluator
        original_get = registry.get

        def mock_get(name):
            if name == "custom_evaluator":
                return mock_evaluator
            return original_get(name)

        monkeypatch.setattr(registry, "get", mock_get)

        try:
            # Access the custom evaluator
            custom = getattr(evaluators, "custom_evaluator")
            assert custom is mock_evaluator

            # Verify it works
            result = custom("test", "test")
            assert result.name == "custom"
            assert result.value is True
        finally:
            registry.get = original_get

    def test_evaluators_dir(self):
        """Test __dir__ includes all evaluators."""
        from dotevals import evaluators

        dir_contents = dir(evaluators)

        # Check __all__ exports are included
        assert "evaluator" in dir_contents
        assert "get_metadata" in dir_contents
        assert "registry" in dir_contents

        # Check built-in evaluators are included
        assert "exact_match" in dir_contents
        assert "numeric_match" in dir_contents
        assert "valid_json" in dir_contents
        assert "ast_evaluation" in dir_contents

    def test_evaluators_dir_with_plugins(self, monkeypatch):
        """Test __dir__ includes plugin evaluators."""

        from dotevals import evaluators
        from dotevals.evaluators.registry import registry

        # Mock list_evaluators to include plugin evaluators
        original_list = registry.list_evaluators

        def mock_list():
            base_list = original_list()
            return base_list + ["plugin_evaluator1", "plugin_evaluator2"]

        monkeypatch.setattr(registry, "list_evaluators", mock_list)

        try:
            dir_contents = dir(evaluators)

            # Check plugin evaluators are included
            assert "plugin_evaluator1" in dir_contents
            assert "plugin_evaluator2" in dir_contents
        finally:
            registry.list_evaluators = original_list
