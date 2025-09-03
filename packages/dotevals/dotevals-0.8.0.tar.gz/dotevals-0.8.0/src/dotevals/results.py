import time
from dataclasses import dataclass, field
from enum import Enum

from dotevals.metrics import Metric
from dotevals.types import DatasetRow, Metadata, ScoreValue


class EvaluationStatus(Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class EvaluationMetadata:
    evaluation_name: str
    status: EvaluationStatus
    started_at: float
    metadata: dict[str, str] = field(default_factory=dict)
    completed_at: float | None = None


@dataclass
class Result:
    """A transient data object returned by an evaluation function."""

    scores: list["Score"]
    model_response: str | None = None
    prompt: str | None = None

    def __init__(
        self,
        *scores: "Score",
        model_response: str | None = None,
        prompt: str | None = None,
    ) -> None:
        self.scores = list(scores)
        self.model_response = model_response
        self.prompt = prompt


@dataclass
class Score:
    name: str
    value: ScoreValue
    metrics: list[Metric]
    metadata: Metadata = field(default_factory=dict)


@dataclass
class Record:
    item_id: int
    dataset_row: DatasetRow
    prompt: str | None
    model_response: str | None
    scores: list[Score]
    error: str | None = None
    timestamp: float = field(default_factory=time.time)
    dataset_name: str | None = None
    dataset_class: str | None = None
