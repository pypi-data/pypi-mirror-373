"""Custom exceptions for dotevals."""


class DotEvalError(Exception):
    """Base exception for all dotevals errors."""

    pass


class EvaluationError(DotEvalError):
    """Raised when an evaluation fails."""

    pass


class StorageError(DotEvalError):
    """Base exception for storage-related errors."""

    pass


class ExperimentNotFoundError(StorageError, FileNotFoundError):
    """Raised when an experiment doesn't exist."""

    def __init__(self, experiment_name: str):
        self.experiment_name = experiment_name
        super().__init__(f"Experiment '{experiment_name}' not found")


class ExperimentExistsError(StorageError, FileExistsError):
    """Raised when trying to create an experiment that already exists."""

    def __init__(self, experiment_name: str):
        self.experiment_name = experiment_name
        super().__init__(f"Experiment '{experiment_name}' already exists")


class EvaluationNotFoundError(StorageError, FileNotFoundError):
    """Raised when an evaluation doesn't exist."""

    def __init__(self, experiment_name: str, evaluation_name: str):
        self.experiment_name = experiment_name
        self.evaluation_name = evaluation_name
        super().__init__(
            f"Evaluation '{evaluation_name}' not found in experiment '{experiment_name}'"
        )


class PluginError(DotEvalError):
    """Base exception for plugin-related errors."""

    pass


class PluginNotFoundError(PluginError, ModuleNotFoundError):
    """Raised when a plugin is not found."""

    def __init__(self, plugin_type: str, plugin_name: str):
        self.plugin_type = plugin_type
        self.plugin_name = plugin_name
        super().__init__(f"{plugin_type} plugin '{plugin_name}' not found")


class PluginLoadError(PluginError, ImportError):
    """Raised when a plugin fails to load."""

    def __init__(self, plugin_name: str, original_error: Exception):
        self.plugin_name = plugin_name
        self.original_error = original_error
        super().__init__(f"Failed to load plugin '{plugin_name}': {original_error}")


class DatasetError(DotEvalError):
    """Base exception for dataset-related errors."""

    pass


class DatasetNotFoundError(DatasetError, LookupError):
    """Raised when a dataset is not found."""

    def __init__(self, dataset_name: str):
        self.dataset_name = dataset_name
        super().__init__(f"Dataset '{dataset_name}' not found")


class ConfigurationError(DotEvalError, ValueError):
    """Raised when there's a configuration issue."""

    pass


class MetricError(DotEvalError):
    """Base exception for metric-related errors."""

    pass


class EvaluatorError(DotEvalError):
    """Base exception for evaluator-related errors."""

    pass


class InvalidResultError(EvaluatorError, TypeError):
    """Raised when an evaluator returns an invalid result."""

    def __init__(self, evaluator_name: str, result_type: type):
        self.evaluator_name = evaluator_name
        self.result_type = result_type
        super().__init__(
            f"Evaluator '{evaluator_name}' returned invalid result type {result_type.__name__}. "
            "Evaluators must return Result objects."
        )
