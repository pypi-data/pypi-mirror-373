"""Example of using the BFCL dataset for function calling evaluation.

This example requires the dotevals-datasets plugin to be installed:
    pip install dotevals-datasets

The BFCL (Berkeley Function Calling Leaderboard) dataset evaluates a model's
ability to correctly call functions based on natural language queries.

It has three variants:
- simple: Single function selection
- multiple: Select from multiple available functions
- parallel: Make multiple function calls in parallel
"""

import json

from dotevals import Result, foreach
from dotevals.evaluators import exact_match


def generate_function_call(question, available_functions):
    """Placeholder for model function calling.

    In practice, you would use your model here, e.g.:
    response = model.generate(
        question,
        tools=available_functions,
        tool_choice="auto"
    )
    """
    # For demo purposes, return empty list
    return []


@foreach.bfcl("simple")
def eval_bfcl_simple(question, schema, answer):
    """Evaluate simple function calling (single function selection).

    Args:
        question: User's natural language query
        schema: JSON string with available function definitions
        answer: JSON string with expected function call(s)
    """
    # Parse schemas and expected answer
    available_functions = json.loads(schema)
    expected_calls = json.loads(answer)

    # Generate function calls with your model
    response = generate_function_call(question, available_functions)

    # Return exact match score
    return exact_match(response, expected_calls)


@foreach.bfcl("multiple")
def eval_bfcl_multiple(question, schema, answer):
    """Evaluate multiple function selection.

    Tests if the model can select the right function from many options.
    """
    available_functions = json.loads(schema)
    expected_calls = json.loads(answer)

    response = generate_function_call(question, available_functions)

    return exact_match(response, expected_calls)


@foreach.bfcl("parallel")
def eval_bfcl_parallel(question, schema, answer):
    """Evaluate parallel function calling.

    Tests if the model can make multiple function calls for one query.
    """
    available_functions = json.loads(schema)
    expected_calls = json.loads(answer)

    response = generate_function_call(question, available_functions)

    # For parallel calls, order might not matter
    # You could implement a more sophisticated comparison here
    return exact_match(response, expected_calls)


# Advanced example with partial credit scoring
@foreach.bfcl("simple")
def eval_bfcl_with_partial_credit(question, schema, answer):
    """Evaluate with partial credit for correct function name selection.

    This gives:
    - 0.5 points for selecting the correct function
    - 0.5 points for correct parameters
    """
    available_functions = json.loads(schema)
    expected_calls = json.loads(answer)

    response = generate_function_call(question, available_functions)

    score = 0.0

    if response and expected_calls:
        # Extract function names
        response_names = {list(call.keys())[0] for call in response}
        expected_names = {list(call.keys())[0] for call in expected_calls}

        # Partial credit for correct function selection
        if response_names == expected_names:
            score = 0.5

            # Full credit if parameters also match
            if response == expected_calls:
                score = 1.0

    return Result(
        prompt=question,
        response=str(response),
        scores={
            "exact_match": score == 1.0,
            "partial_credit": score,
            "function_name_correct": score >= 0.5,
        },
    )


if __name__ == "__main__":
    # To run these evaluations:
    # pytest bfcl.py::eval_bfcl_simple --experiment bfcl_simple
    # pytest bfcl.py::eval_bfcl_multiple --experiment bfcl_multiple
    # pytest bfcl.py::eval_bfcl_parallel --experiment bfcl_parallel

    print("Run with pytest to evaluate:")
    print("  pytest bfcl.py::eval_bfcl_simple --experiment my_bfcl_eval")
    print("\nView results with:")
    print("  dotevals show my_bfcl_eval")
