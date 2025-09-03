import random

import datasets
import outlines
import pytest
from outlines import Template, models

from dotevals import foreach
from dotevals.evaluators import exact_match


@pytest.fixture
def template():
    template = Template.from_string(
        """
    Q: {{question}}
    (A){{choices[0]}}
    (B){{choices[1]}}
    (C){{choices[2]}}
    (D){{choices[3]}}
    After your reasoning, provide your final, single letter choice, formatted as "The answer is (X)."
    """
    )
    return template


@pytest.fixture()
def generator():
    model = models.llamacpp(
        repo_id="M4-ai/TinyMistral-248M-v2-Instruct-GGUF",
        filename="TinyMistral-248M-v2-Instruct.Q4_K_M.gguf",
        model_kwargs={"n_ctx": 2048, "verbose": False},
    )
    generator = outlines.generate.regex(model, "[ABCD]")

    return generator


def gpqa_dataset():
    dataset = datasets.load_dataset(
        path="Idavidrein/gpqa", name="gpqa_diamond", split="train"
    )
    questions = dataset["Question"]

    multiple_choices = [
        list(x)
        for x in list(
            zip(
                *[
                    dataset["Correct Answer"],
                    dataset["Incorrect Answer 1"],
                    dataset["Incorrect Answer 2"],
                    dataset["Incorrect Answer 3"],
                ]
            )
        )
    ]
    answers = dataset["Correct Answer"]
    for question, multiple_choice, answer in zip(questions, multiple_choices, answers):
        random.shuffle(multiple_choice)
        correct_letter = "ABCD"[multiple_choice.index(answer)]
        yield question, multiple_choice, correct_letter


@foreach("question,choices,answer", gpqa_dataset())
def eval_gpqa(question, choices, answer, generator, template):
    prompt = template(question=question, choices=choices)
    result = generator(prompt, max_tokens=1)
    score = exact_match(result, answer)

    return score
