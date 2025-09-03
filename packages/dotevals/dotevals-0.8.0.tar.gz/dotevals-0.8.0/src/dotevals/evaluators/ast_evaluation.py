import json
import re
from collections.abc import Callable
from typing import Any

from dotevals.evaluators.base import evaluator, valid_json
from dotevals.metrics import accuracy


@evaluator(metrics=accuracy())
def ast_evaluation(
    result: dict[str, Any],
    expected: list[dict[str, Any]],
    schema: list[dict[str, Any]],
) -> bool:
    """Evaluate if a function call matches the expected schema and parameters."""
    if not result or not expected or not schema or len(result) != 1:
        return False

    model_output = result
    possible_answer = expected[0]
    function_description = schema[0]
    return is_function_call_valid(function_description, model_output, possible_answer)


def normalize_string(s):
    """Normalize string by removing special characters and converting to lowercase."""
    return re.sub(r"[ \,\./\-_\*\^]", "", str(s)).lower().replace("'", '"')


def recursive_normalize(obj: Any) -> Any:
    """
    Recursively normalize all string values in a nested structure.

    Args:
        obj: The object to normalize

    Returns:
        The normalized object with string values normalized
    """
    return recursive_map(
        obj, lambda val: normalize_string(val) if isinstance(val, str) else val
    )


def is_dict_match(actual_value, expected_value):
    """Check if the actual dictionary matches any of the expected dictionaries"""
    if isinstance(expected_value, (set | list)):
        expected_dicts = list(expected_value)
    else:
        expected_dicts = [expected_value]

    actual_norm = recursive_normalize(actual_value)
    for expected_dict in expected_dicts:
        if expected_dict == "":
            continue
        if actual_norm == recursive_normalize(expected_dict):
            return True
    if all(ed == "" for ed in expected_dicts):
        return True
    return False


def compare_param_value(param_value, expected_param_value):
    """Compare a parameter value to the expected value."""
    if isinstance(expected_param_value, dict) and isinstance(param_value, dict):
        return is_dict_match(param_value, expected_param_value)
    elif isinstance(expected_param_value, str) and isinstance(param_value, str):
        return normalize_string(param_value) == normalize_string(expected_param_value)
    elif isinstance(expected_param_value, (set | list)):
        return param_value in expected_param_value
    else:
        return param_value == expected_param_value


def is_function_call_valid(schema, model_output, expected_answer):
    """Validate that the function call matches the schema and expected answer."""
    expected_answer = list(expected_answer.values())[0]
    function_name = schema["name"]
    parameter_definitions = schema["parameters"]["properties"]
    required_parameters = set(schema["parameters"]["required"])

    if function_name not in model_output:
        return False

    model_params = model_output[function_name]

    if not required_parameters.issubset(model_params):
        return False

    try:
        json.dumps({function_name: model_params})
    except Exception:
        return False

    if not valid_json({function_name: model_params}, schema):
        return False  # pragma: no cover

    for param_name, param_value in model_params.items():
        if param_name not in parameter_definitions or param_name not in expected_answer:
            return False

        expected_param_value = expected_answer[param_name]
        if not compare_param_value(param_value, expected_param_value):
            return False

    for param_name, expected_param_value in expected_answer.items():
        if param_name not in model_params:
            if (
                isinstance(expected_param_value, (set | list))
                and "" not in expected_param_value
            ) or (
                not isinstance(expected_param_value, (set | list))
                and expected_param_value != ""
            ):
                return False

    return True


def recursive_map(obj: Any, transform_func: Callable[[Any], Any]) -> Any:
    """
    Recursively apply a transformation function to all values in a nested structure.

    This function traverses through dictionaries, lists, sets, and tuples,
    applying the transform_func to each value it encounters.

    Args:
        obj: The object to transform
        transform_func: Function to apply to each value

    Returns:
        The object with all values transformed by transform_func
    """
    if isinstance(obj, dict):
        return {k: recursive_map(v, transform_func) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [recursive_map(x, transform_func) for x in obj]
    elif isinstance(obj, set):
        return {recursive_map(x, transform_func) for x in obj}
    elif isinstance(obj, tuple):
        return tuple(recursive_map(x, transform_func) for x in obj)
    else:
        return transform_func(obj)
