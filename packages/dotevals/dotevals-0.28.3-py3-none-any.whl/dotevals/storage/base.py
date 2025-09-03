from abc import ABC, abstractmethod

from dotevals.results import EvaluationMetadata, EvaluationStatus, Record

__all__ = ["Storage"]


class Storage(ABC):
    """Abstract storage interface"""

    @abstractmethod
    def create_experiment(self, experiment_name: str) -> None:
        """Create an experiment. Should be idempotent - if experiment exists, do nothing."""
        pass

    @abstractmethod
    def delete_experiment(self, experiment_name: str) -> None:
        pass

    @abstractmethod
    def rename_experiment(self, old_name: str, new_name: str) -> None:
        pass

    @abstractmethod
    def list_experiments(self) -> list[str]:
        pass

    @abstractmethod
    def create_evaluation(
        self, experiment_name: str, evaluation: EvaluationMetadata
    ) -> None:
        pass

    @abstractmethod
    def load_evaluation(
        self, experiment_name: str, evaluation_name: str
    ) -> EvaluationMetadata | None:
        pass

    @abstractmethod
    def update_evaluation_status(
        self, experiment_name: str, evaluation_name: str, status: EvaluationStatus
    ) -> None:
        pass

    @abstractmethod
    def completed_items(self, experiment_name: str, evaluation_name: str) -> list[int]:
        pass

    @abstractmethod
    def list_evaluations(self, experiment_name: str) -> list[str]:
        pass

    @abstractmethod
    def add_results(
        self,
        experiment_name: str,
        evaluation_name: str,
        results: list[Record],
    ) -> None:
        pass

    @abstractmethod
    def get_results(self, experiment_name: str, evaluation_name: str) -> list[Record]:
        pass

    @abstractmethod
    def remove_error_result(
        self, experiment_name: str, evaluation_name: str, item_id: int
    ) -> None:
        """Remove an errored result for a specific item that will be retried."""
        pass

    def remove_error_results_batch(
        self, experiment_name: str, evaluation_name: str, item_ids: list[int]
    ) -> None:
        """Remove multiple errored results in a batch.

        Default implementation calls remove_error_result for each item.
        Storage backends should override this for better performance.
        """
        for item_id in item_ids:
            self.remove_error_result(experiment_name, evaluation_name, item_id)
