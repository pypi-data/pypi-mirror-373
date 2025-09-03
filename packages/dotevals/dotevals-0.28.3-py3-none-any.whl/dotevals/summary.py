"""Summary and aggregation functionality for evaluation results."""

from collections import defaultdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dotevals.metrics import Metric
    from dotevals.results import Record, ScoreValue


class EvaluationSummary:
    """Aggregated results of a full evaluation."""

    def __init__(self, results: list["Record"]) -> None:
        self.results = results
        self.summary = self.compute_summary()

    def compute_summary(self) -> dict[str, dict[str, float | int]]:
        summary: dict[str, dict[str, float | int]] = defaultdict(dict)

        # First pass: determine the expected score structure from successful results
        expected_scores: list[tuple[str, list[tuple[str, Metric]]]] = []
        for result in self.results:
            if result.error is None and result.scores:
                expected_scores = [
                    (score.name, [(m.__name__, m) for m in score.metrics])
                    for score in result.scores
                ]
                break

        # Regorganize the results by evaluator and metric NAME (not object)
        # Also keep track of a metric function to use for computation
        aggregated_results: dict[str, dict[str, tuple[list[ScoreValue], Metric]]] = (
            defaultdict(dict)
        )

        for result in self.results:
            if result.error is not None:
                # For error cases, add False values for each expected score
                for score_name, metrics in expected_scores:
                    for metric_name, metric_func in metrics:
                        if metric_name not in aggregated_results[score_name]:
                            aggregated_results[score_name][metric_name] = (
                                [],
                                metric_func,
                            )
                        aggregated_results[score_name][metric_name][0].append(False)
            else:
                # For successful cases, use actual scores
                for score in result.scores:
                    for metric in score.metrics:
                        metric_name = metric.__name__
                        if metric_name not in aggregated_results[score.name]:
                            aggregated_results[score.name][metric_name] = ([], metric)
                        aggregated_results[score.name][metric_name][0].append(
                            score.value
                        )

        for evaluator_name, metrics_data in aggregated_results.items():
            for metric_name, (values, metric_func) in metrics_data.items():
                summary[evaluator_name][metric_name] = metric_func(values)  # type: ignore[arg-type]

        return summary
