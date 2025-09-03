"""Example of evaluating GSM8K math problems.

This example requires the dotevals-datasets plugin to be installed:
    pip install dotevals-datasets

It also requires outlines for structured generation:
    pip install outlines
"""

import functools
import itertools

import pytest
from outlines import Template, generate, models

from dotevals import foreach
from dotevals.evaluators import numeric_match


@pytest.fixture
def template():
    """Build the prompt template with 4 shots taken from the training set."""
    template = Template.from_string(
        """{% for example in examples %}
    Q: {{ example.question }}
    A: {{ example.reasoning }}
    #### {{ example.answer }}
    {% endfor %}

    Q: {{ question }}
    A:"""
    )

    # Get 4 examples from the training set
    # In a real scenario, you might load these from the training split:
    # @foreach.gsm8k("train") to get examples
    # For this demo, we use hardcoded examples
    examples = [
        {
            "question": "Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?",
            "reasoning": "Natalia sold 48/2 = 24 clips in May. Natalia sold 48 + 24 = 72 clips altogether in April and May.",
            "answer": "72",
        },
        {
            "question": "Weng earns $12 an hour for babysitting. Yesterday, she just did 50 minutes of babysitting. How much did she earn?",
            "reasoning": "Weng earns 12/60 = $0.2 per minute. Working 50 minutes, she earned 0.2 x 50 = $10.",
            "answer": "10",
        },
        {
            "question": "Betty is saving money for a new wallet which costs $100. Betty has only half of the money she needs. Her parents decided to give her $15 for that purpose, and her grandparents twice as much as her parents. How much more money does Betty need to buy the wallet?",
            "reasoning": "Betty has 100 / 2 = $50. Betty's grandparents gave her 15 * 2 = $30. So Betty has 50 + 15 + 30 = $95. Betty needs 100 - 95 = $5 more.",
            "answer": "5",
        },
        {
            "question": "Julie is reading a 120-page book. Yesterday, she was able to read 12 pages and today, she read twice as many pages as yesterday. If she wants to read half of the remaining pages tomorrow, how many pages should she read?",
            "reasoning": "Julie read 12 x 2 = 24 pages today. So she has read a total of 12 + 24 = 36 pages. There are 120 - 36 = 84 pages left. So Julie should read 84 / 2 = 42 pages tomorrow.",
            "answer": "42",
        },
    ]

    return functools.partial(template, examples=examples)


@pytest.fixture
def generator():
    """Build the generator once."""
    model = models.llamacpp(
        repo_id="M4-ai/TinyMistral-248M-v2-Instruct-GGUF",
        filename="TinyMistral-248M-v2-Instruct.Q4_K_M.gguf",
        model_kwargs={"n_ctx": 2048, "verbose": False},
    )
    generator = generate.regex(model, r"[1-9][0-9]*")

    return generator


@foreach.gsm8k("test")
def eval_gsm8k(question, reasoning, answer, generator, template):
    """Evaluate GSM8K using the three-column format."""
    prompt = template(question=question)
    result = generator(prompt, max_tokens=10)
    score = numeric_match(result, answer)

    return score
