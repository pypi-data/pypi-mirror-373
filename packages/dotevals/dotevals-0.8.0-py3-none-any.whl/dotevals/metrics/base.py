from collections.abc import Callable
from typing import Any

Metric = Callable[[list[bool]], float]


def metric(metric_func: Callable[..., Metric]) -> Callable[..., Metric]:
    """Decorator for metrics.

    This decorator is used to create metric functions that can be attached to evaluators.
    The decorated function should return a metric function that takes a list of boolean
    values and returns a float score.

    Args:
        metric_func: Function whose name will be used when attaching to evaluator.
            The function should return another function that takes a list[bool] and returns a float.

    Returns:
        A wrapper function that preserves the metric name and can be called to create metric instances.

    Examples:
        ```python
        @metric
        def custom_accuracy():
            def metric_impl(scores: list[bool]) -> float:
                return sum(scores) / len(scores) if scores else 0.0
            return metric_impl

        accuracy_metric = custom_accuracy()
        accuracy_metric([True, False, True])  # Returns: 0.6667
        ```
    """

    def create_metric_wrapper(
        metric_func: Callable[..., Metric], name: str
    ) -> Callable[..., Metric]:
        def metric_wrapper(*args: Any, **kwargs: Any) -> Metric:
            metric = metric_func(*args, **kwargs)
            metric.__name__ = name
            return metric

        return metric_wrapper

    metric_name = getattr(metric_func, "__name__")
    wrapper = create_metric_wrapper(metric_func, metric_name)
    wrapper.__name__ = metric_name

    return wrapper


@metric
def accuracy() -> Metric:
    """Metric for accuracy.

    Takes a list of boolean values and returns the percentage of the list that are True.

    Returns:
        A metric function that computes accuracy as the mean of boolean scores.
    """

    def metric(scores: list[bool]) -> float:
        if len(scores) == 0:
            return 0
        total = 0.0
        for score in scores:
            total += float(score)
        return total / float(len(scores))

    return metric


registry = {"accuracy": accuracy()}
