from abc import ABC, abstractmethod
from collections import defaultdict
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from dotevals.executors.base import DatasetInfo
    from dotevals.results import Record

from rich.console import Console
from rich.live import Live
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table
from rich.text import Text


def _is_running_under_pytest() -> bool:
    """Check if we're currently running under pytest.

    Returns:
        bool: True if running under pytest, False otherwise.

    Note:
        This is used to disable progress bars during pytest execution
        to avoid interfering with test output.
    """
    try:
        import sys

        return "pytest" in sys.modules
    except ImportError:
        return False


class ProgressTracker:
    """Self-contained progress tracker for a single evaluation.

    This class encapsulates all logic for tracking a single evaluation's progress,
    including completion counting, error tracking, and metrics calculation.
    It is responsible for its own state management and formatting.

    Attributes:
        evaluation_name (str): Name of the evaluation being tracked
        total_items (int, optional): Total number of items to process
        completed (int): Number of completed items
        error_count (int): Number of items that resulted in errors
        task_id (str, optional): Rich progress task ID for multi-evaluation mode
        metrics (dict): Live metrics for single evaluation mode
    """

    def __init__(
        self,
        evaluation_name: str,
        total_items: int | None = None,
        task_id: str | None = None,
    ) -> None:
        """Initialize progress tracker.

        Args:
            evaluation_name (str): Name of the evaluation being tracked
            total_items (int, optional): Total number of items expected.
                If None, progress is tracked as a spinner.
            task_id (str, optional): Rich progress task ID for multi-evaluation mode
        """
        self.evaluation_name = evaluation_name
        self.total_items = total_items
        self.completed = 0
        self.error_count = 0
        self.task_id = task_id
        self.metrics: dict[str, float] = {}
        self._all_results: list[Record] = []  # For metrics calculation

    def update_progress(
        self, result: Optional["Record"] = None, completed_count: int | None = None
    ) -> None:
        """Update progress for this evaluation.

        Args:
            result (Record, optional): Latest evaluation result
            completed_count (int, optional): Set absolute completion count
        """
        if completed_count is not None:
            self.completed = completed_count
        else:
            self.completed += 1

        # Track errors
        if result and hasattr(result, "error") and result.error is not None:
            self.error_count += 1

        # Update metrics
        if result:
            self._update_metrics(result)

    def _update_metrics(self, result: "Record") -> None:
        """Calculate live metrics for this evaluation.

        Args:
            result (Record): The latest evaluation result to include
        """
        self._all_results.append(result)

        # Determine expected score structure from successful results
        expected_scores = []
        for res in self._all_results:
            if (
                hasattr(res, "error")
                and res.error is None
                and hasattr(res, "result")
                and res.result.scores
            ):
                expected_scores = [
                    (score.name, score.metrics)
                    for score in res.result.scores
                    if hasattr(score, "name")
                ]
                break

        # Recalculate metrics from all results
        aggregated_results: dict[str, dict[Any, list[Any]]] = defaultdict(
            lambda: defaultdict(list)
        )
        for res in self._all_results:
            if hasattr(res, "error") and res.error is not None:
                # For error cases, add False values for each expected score
                for score_name, metrics in expected_scores:
                    for metric in metrics:
                        aggregated_results[score_name][metric].append(False)
            else:
                # For successful cases, use actual scores
                if hasattr(res, "result") and res.result.scores:
                    for score in res.result.scores:
                        for metric in score.metrics:
                            aggregated_results[score.name][metric].append(score.value)

        # Compute and store metrics
        computed_metrics = {}
        for evaluator_name, metrics_values in aggregated_results.items():
            for metric_func, values in metrics_values.items():
                if values:  # Only compute if we have values
                    metric_name = metric_func.__name__.replace("_", " ").title()
                    computed_metrics[metric_name] = metric_func(values)

        self.metrics = computed_metrics

    def get_error_text(self) -> str:
        """Get formatted error text for display.

        Returns:
            str: Formatted error text or empty string if no errors
        """
        if self.error_count > 0:
            return f" ! {self.error_count} error{'s' if self.error_count != 1 else ''}"
        return ""

    def format_metrics_for_display(self) -> str:
        """Format metrics for display in single evaluation mode.

        Returns:
            str: Formatted metrics text or empty string if no metrics
        """
        if not self.metrics:
            return ""

        metrics_parts = []
        for name, value in self.metrics.items():
            if isinstance(value, float):
                metrics_parts.append(f"{name}: {value:.1%}")
            else:
                metrics_parts.append(f"{name}: {value}")

        return " • ".join(metrics_parts) if metrics_parts else ""


class BaseProgressManager(ABC):
    """Base class defining the progress manager interface.

    This defines the common contract that all progress managers must implement,
    while allowing different implementations for different use cases.
    """

    @abstractmethod
    def start_evaluation(
        self,
        evaluation_name: str,
        total_items: int | None = None,
        dataset_info: Any = None,
    ) -> None:
        """Start tracking progress for a specific evaluation."""
        pass

    @abstractmethod
    def update_evaluation_progress(
        self,
        evaluation_name: str,
        completed_count: int | None = None,
        result: Optional["Record"] = None,
    ) -> None:
        """Update progress for a specific evaluation."""
        pass

    @abstractmethod
    def finish(self) -> None:
        """Finish progress tracking and clean up resources."""
        pass

    def __enter__(self) -> "BaseProgressManager":
        """Enter context manager."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager."""
        pass


class MultiProgress(BaseProgressManager):
    """Progress display for multiple evaluations (pytest mode).

    This manager handles multiple concurrent evaluations, displaying
    each as a separate progress bar in a shared Rich Progress display.
    Designed for pytest execution where multiple evaluation functions
    run in sequence or parallel.

    Attributes:
        evaluations (dict): Map of evaluation names to ProgressTracker instances
        active (bool): Whether progress tracking is currently active
        progress (Progress): Rich Progress instance for display
        live (Live): Rich Live instance for real-time updates
    """

    def __init__(self):
        """Initialize multi-evaluation progress manager."""
        self.evaluations = {}
        self.active = False
        self.progress = None
        self.live = None

    def start(self, total_evaluations=None):
        """Start the multi-evaluation progress display.

        Args:
            total_evaluations (int, optional): Expected number of evaluations.
        """
        self.active = True
        self.total_evaluations = total_evaluations

        # Set up multi-evaluation display
        self.progress = Progress(
            TextColumn("✨ {task.description}"),
            GreenCompletedBarColumn(bar_width=60),
            MofNCompleteColumn(),
            TextColumn("• Elapsed:"),
            TimeElapsedColumn(),
            TextColumn("• ETA:"),
            TimeRemainingColumn(),
            TextColumn("[bold red]{task.fields[error_text]}[/bold red]"),
        )
        self.live = Live(self.progress, console=Console(), refresh_per_second=10)
        self.live.start()

    def start_evaluation(self, evaluation_name, total_items=None, dataset_info=None):
        """Add a new evaluation to the multi-evaluation display.

        Args:
            evaluation_name (str): Unique name for this evaluation
            total_items (int, optional): Total number of items to process.
            dataset_info (dict, optional): Additional dataset information (unused).
        """
        task_id = None
        if self.progress:
            task_id = self.progress.add_task(
                evaluation_name,
                total=total_items,  # Use None for unknown sizes
                error_text="",
            )

        tracker = ProgressTracker(evaluation_name, total_items, task_id)
        self.evaluations[evaluation_name] = tracker

    def update_evaluation_progress(
        self, evaluation_name, completed_count=None, result=None
    ):
        """Update progress for a specific evaluation.

        Args:
            evaluation_name (str): Name of the evaluation to update
            completed_count (int, optional): Set absolute completion count.
            result (Record, optional): The evaluation result object.
        """
        if evaluation_name not in self.evaluations:
            return

        tracker = self.evaluations[evaluation_name]
        tracker.update_progress(result=result, completed_count=completed_count)

        # Update the Rich progress display
        if self.progress and tracker.task_id is not None:
            self.progress.update(
                tracker.task_id,
                completed=tracker.completed,
                error_text=tracker.get_error_text(),
            )

    def finish(self):
        """Finish progress tracking and clean up resources."""
        self.active = False
        self.evaluations.clear()

        # Stop display
        if self.live:
            self.live.stop()
            self.live = None
        self.progress = None


class SingleProgress(BaseProgressManager):
    """Progress display for single evaluation with metrics (programmatic mode).

    This manager handles a single evaluation, displaying a progress bar
    with live metrics underneath. Designed for programmatic execution
    where one evaluation runs at a time with detailed feedback.

    Supports context manager usage for automatic cleanup.

    Attributes:
        tracker (ProgressTracker): The single evaluation tracker
        progress (Progress): Rich Progress instance for display
        live (Live): Rich Live instance for real-time updates
    """

    def __init__(self):
        """Initialize single evaluation progress manager."""
        self.tracker = None
        self.progress = None
        self.live = None

    def start_evaluation(self, evaluation_name, total_items=None, dataset_info=None):
        """Start tracking progress for the single evaluation.

        Args:
            evaluation_name (str): Name for this evaluation
            total_items (int, optional): Total number of items to process.
            dataset_info (dict, optional): Additional dataset information for display.
        """
        self.tracker = ProgressTracker(evaluation_name, total_items)

        # Don't show progress bars when running under pytest
        if not _is_running_under_pytest():
            self._setup_display(evaluation_name, total_items, dataset_info)

    def _setup_display(self, evaluation_name, total_items, dataset_info):
        """Set up the Rich progress display.

        Args:
            evaluation_name (str): Name of the evaluation
            total_items (int, optional): Total number of items
            dataset_info (dict, optional): Dataset information for display
        """
        total_count = total_items
        if not total_count and dataset_info:
            total_count = dataset_info.get("total_rows")

        if total_count:
            # Known size - use progress bar with ETA
            self.progress = Progress(
                TextColumn("✨ {task.description}"),
                GreenCompletedBarColumn(bar_width=60),
                MofNCompleteColumn(),
                TextColumn("• Elapsed:"),
                TimeElapsedColumn(),
                TextColumn("• ETA:"),
                TimeRemainingColumn(),
                TextColumn("[bold red]{task.fields[error_text]}[/bold red]"),
                console=Console(),
                expand=False,
            )
            self.main_task = self.progress.add_task(
                evaluation_name, total=total_count, error_text=""
            )
        else:
            # Unknown size - use spinner with completion counter
            self.progress = Progress(
                SpinnerColumn(),
                TextColumn("✨ {task.description}"),
                TextColumn("• {task.completed:,} completed"),
                TimeElapsedColumn(),
                TextColumn("[bold red]{task.fields[error_text]}[/bold red]"),
                console=Console(),
                expand=False,
            )
            self.main_task = self.progress.add_task(
                evaluation_name, total=None, error_text=""
            )

        self.live = Live(self._build_display(), console=Console(), refresh_per_second=4)
        self.live.start()

    def update_evaluation_progress(
        self, evaluation_name, completed_count=None, result=None
    ):
        """Update progress for the single evaluation.

        Args:
            evaluation_name (str): Name of the evaluation (must match tracker)
            completed_count (int, optional): Set absolute completion count.
            result (Record, optional): The evaluation result object.
        """
        if not self.tracker or self.tracker.evaluation_name != evaluation_name:
            return

        self.tracker.update_progress(result=result, completed_count=completed_count)

        # Update the Rich progress display
        if self.progress and hasattr(self, "main_task"):
            self.progress.update(
                self.main_task,
                completed=self.tracker.completed,
                error_text=self.tracker.get_error_text(),
            )

            if self.live:
                self.live.update(self._build_display())

    def _build_display(self):
        """Build the combined progress and metrics display.

        Returns:
            Table: Rich table containing progress bar and metrics
        """
        if not self.progress:
            return ""

        table = Table.grid(padding=(0, 0))
        table.add_column()

        # Add main progress
        table.add_row(self.progress)

        # Add metrics row if available
        if self.tracker:
            metrics_text = self.tracker.format_metrics_for_display()
            if metrics_text:
                table.add_row(Text(metrics_text, style="dim"))

        return table

    def finish(self):
        """Finish progress tracking and clean up resources."""
        # Stop display
        if self.live:
            self.live.stop()
            self.live = None
        self.progress = None
        self.tracker = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager and clean up resources."""
        self.finish()


class GreenCompletedBarColumn(BarColumn):
    """A progress bar column that stays green when completed.

    This custom Rich progress bar column ensures that completed progress
    bars remain green instead of reverting to the default style.
    """

    def __init__(self, bar_width=60):
        """Initialize green completed bar column.

        Args:
            bar_width (int): Width of the progress bar in characters (default: 60)
        """
        super().__init__(
            bar_width=bar_width, complete_style="green", finished_style="green"
        )


def get_dataset_info(dataset: Any) -> "DatasetInfo":
    """Extract dataset information for progress display.

    Args:
        dataset: Dataset object, iterator, or any iterable

    Returns:
        dict: Dictionary containing dataset information with keys:
            - 'name' (str): Display name for the dataset
            - 'total_rows' (int or None): Total number of rows if determinable
    """
    info: DatasetInfo = {"name": "Dataset", "total_rows": None}

    # Check if this is a Dataset instance from the registry
    if hasattr(dataset, "name") and hasattr(dataset, "num_rows"):
        info.update(
            {
                "name": dataset.name.upper(),
                "total_rows": dataset.num_rows,
            }
        )
    # Fallback to size estimation for direct iterators
    elif hasattr(dataset, "__len__"):
        try:
            info["total_rows"] = len(dataset)
        except (TypeError, AttributeError):
            pass

    return info
