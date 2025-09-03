import inspect
import json
from collections.abc import Callable
from typing import Any, TypeAlias

from dotevals.metrics import Metric, accuracy
from dotevals.results import Score

# Type for comparable values in evaluators
Comparable: TypeAlias = str | int | float | bool | None


def evaluator(
    metrics: Metric | list[Metric],
) -> Callable[[Callable], Callable[..., Score]]:
    """Decorator to convert evaluation functions into evaluators that return Score objects.

    This decorator wraps evaluation functions to automatically create Score objects with
    associated metrics. It handles custom naming and metadata extraction.

    Args:
        metrics: Single metric or list of metrics to apply to the evaluation results.
                Common metrics include accuracy(), precision(), recall(), etc.

    Returns:
        A decorator function that transforms evaluation functions into evaluators.

    Examples:
        ```python
        @evaluator(metrics=accuracy())
        def exact_match(result, expected):
            return result == expected

        @evaluator(metrics=[accuracy(), precision()])
        def fuzzy_match(result, expected, threshold=0.8):
            return similarity_score(result, expected) >= threshold

        # Usage with custom name
        score = exact_match("hello", "hello", name="greeting_match")
        # Returns Score object with name="greeting_match"
        ```
    """
    if not isinstance(metrics, list):
        metrics = [metrics]

    def decorator(func: Callable[..., Any]) -> Callable[..., Score]:
        def wrapper(*args: Any, **kwargs: Any) -> Score:
            # Extract custom name from kwargs if provided
            custom_name = kwargs.pop("name", None)
            value = func(*args, **kwargs)
            metadata = get_metadata(func, *args, **kwargs)

            # Use custom name if provided, otherwise use function name
            score_name = custom_name if custom_name is not None else func.__name__
            return Score(score_name, value, metrics, metadata)

        wrapper.__name__ = func.__name__

        return wrapper

    return decorator


def get_metadata(func: Callable[..., Any], *args: Any, **kwargs: Any) -> dict[str, Any]:
    """Extract metadata from function call by mapping arguments to parameter names.

    This function introspects the function signature to create a mapping of
    parameter names to their values from the function call. This metadata is
    attached to Score objects for debugging and analysis purposes.

    Args:
        func: The function being called
        *args: Positional arguments passed to the function
        **kwargs: Keyword arguments passed to the function

    Returns:
        dict: Mapping of parameter names to their values

    Examples:
        ```python
        def example_func(a, b, c=None):
            pass

        metadata = get_metadata(example_func, 1, 2, c=3)
        # Returns: {'a': 1, 'b': 2, 'c': 3}
        ```
    """
    sig = inspect.signature(func)
    param_names = list(sig.parameters.keys())

    metadata = {}
    for i, arg in enumerate(args):
        if i < len(param_names):
            metadata[param_names[i]] = arg

    metadata.update(kwargs)

    return metadata


@evaluator(metrics=accuracy())
def exact_match(
    result: Comparable, expected: Comparable, name: str | None = None
) -> bool:
    return result == expected


@evaluator(metrics=accuracy())
def numeric_match(
    result: str | int | float, expected: str | int | float, name: str | None = None
) -> bool:
    """Compare numeric values, handling various formats like commas, spaces, and scientific notation.

    Examples:
        ```python
        numeric_match("1234", "1,234") -> True
        numeric_match("1234", "1 234") -> True
        numeric_match("1234", "1.234e3") -> True
        numeric_match("42", 42) -> True
        numeric_match("3.14", 3.14) -> True
        numeric_match("1,234.56", "1234.56") -> True
        numeric_match("1 234 567", "1234567") -> True
        numeric_match("-1,234", "-1234") -> True
        numeric_match("0.50", "0.5") -> True
        numeric_match(" 42 ", "42") -> True
        numeric_match("nan", "nan") -> False
        numeric_match("abc", "123") -> False
        ```
    """
    # Handle None and empty values
    if result is None or expected is None:
        return False

    # Convert to strings for processing
    value_str = str(result).strip()
    expected_str = str(expected).strip()

    # Handle empty strings
    if not value_str or not expected_str:
        return False

    # Try to parse as numbers
    try:
        # Remove thousand separators (commas and spaces)
        # But preserve the space after a minus sign as that's invalid
        def clean_number(s):
            # Check if there's a space after minus sign at the beginning
            if s.startswith("- "):
                # This is invalid, return as-is to let float() fail
                return s
            # Otherwise remove commas and spaces
            return s.replace(",", "").replace(" ", "")

        value_clean = clean_number(value_str)
        expected_clean = clean_number(expected_str)

        # Parse to float
        value_num = float(value_clean)
        expected_num = float(expected_clean)

        # Handle NaN case (NaN != NaN in Python)
        if value_clean.lower() == "nan" and expected_clean.lower() == "nan":
            return False

        # Compare the numeric values
        return value_num == expected_num
    except (ValueError, AttributeError):
        # If parsing fails, values are not numeric
        return False


@evaluator(metrics=accuracy())
def valid_json(result: Any, schema: dict | None = None) -> bool:
    """Check if a value is valid JSON and optionally validate against a JSON schema.

    Args:
        result: The value to check - typically a string containing JSON
        schema: Optional JSON schema dict to validate against

    Examples:
        ```python
        valid_json('{"name": "John"}') -> True
        valid_json('{"name": "John",}') -> False (trailing comma)
        valid_json('["a", "b", "c"]') -> True
        valid_json('123') -> True (valid JSON number)
        valid_json('invalid') -> False

        # With schema validation
        schema = {"type": "object", "required": ["name"]}
        valid_json('{"name": "John"}', schema) -> True
        valid_json('{"age": 30}', schema) -> False (missing required field)
        ```

    Returns:
        True if value is valid JSON (and matches schema if provided), False otherwise
    """
    # Handle None and empty values
    if result is None:
        return False

    # Convert to string
    value_str = str(result).strip()

    # Handle empty strings
    if not value_str:
        return False

    try:
        # Try to parse the JSON
        parsed = json.loads(value_str)

        # If no schema provided, just check if it's valid JSON
        if schema is None:
            return True

        # If schema provided, validate against it using jsonschema
        import jsonschema

        jsonschema.validate(instance=parsed, schema=schema)
        return True

    except (json.JSONDecodeError, ValueError):
        # If parsing fails, it's not valid JSON
        return False
    except jsonschema.ValidationError:
        # JSON is valid but doesn't match schema
        return False
    except jsonschema.SchemaError:
        # The schema itself is invalid
        return False
