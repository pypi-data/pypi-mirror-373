"""Batch executor implementation."""

from collections.abc import Callable, Generator
from typing import Any

from dotevals.executors.base import DatasetInfo, Executor
from dotevals.executors.registry import executor_registry
from dotevals.progress import BaseProgressManager
from dotevals.results import Record
from dotevals.sessions import SessionManager


def _chunk_dataset(
    dataset: list, chunk_size: int | None
) -> Generator[list, None, None]:
    """Chunk dataset into batches.

    Args:
        dataset: The dataset to chunk
        chunk_size: Size of each chunk (None means no chunking - return all as one batch)

    Yields:
        Lists containing items from the dataset
    """
    if chunk_size is None:
        # No chunking - return all items as one batch
        yield dataset
    else:
        # Chunk into specified sizes
        for i in range(0, len(dataset), chunk_size):
            yield dataset[i : i + chunk_size]


class BatchExecutor(Executor):
    """Default Batch executor plugin."""

    @property
    def name(self) -> str:
        return "batch"

    def _execute_sync(
        self,
        eval_fn: Callable,
        columns: list[str],
        dataset_items: list[tuple[int, dict[str, Any] | Exception]],
        session_manager: SessionManager,
        progress_manager: BaseProgressManager,
        dataset_info: DatasetInfo,
        **kwargs: Any,
    ) -> None:
        """Execute synchronous evaluation in batches."""
        batch_size = kwargs.pop("batch_size", None)

        total_items = len(dataset_items)
        progress_manager.start_evaluation(
            dataset_info.get("name", "dataset"), total_items, dataset_info
        )

        # Process items in batches
        for batch in _chunk_dataset(dataset_items, batch_size):
            # Separate valid items from error items
            error_items = [
                (item_id, data)
                for item_id, data in batch
                if isinstance(data, Exception)
            ]
            valid_items = [
                (item_id, data)
                for item_id, data in batch
                if not isinstance(data, Exception)
            ]

            # Process error items first
            for item_id, error in error_items:
                error_record = self._create_error_record(item_id, {}, error)
                session_manager.add_results([error_record])
                progress_manager.update_evaluation_progress(
                    dataset_info.get("name", "dataset"), result=error_record
                )

            # Skip batch if no valid items
            if not valid_items:
                continue

            batch_item_ids = [item_id for item_id, _ in valid_items]
            batch_row_dicts = [row_dict for _, row_dict in valid_items]

            # Prepare batch inputs (lists of values for each column)
            batch_inputs = {
                col: [row[col] for row in batch_row_dicts] for col in columns
            }

            try:
                # Run evaluation on the batch
                result = eval_fn(**batch_inputs, **kwargs)

                # Handle both list of results and single result for entire batch
                if isinstance(result, list):
                    if len(result) != len(valid_items):
                        raise ValueError(
                            f"Batch function returned {len(result)} results but batch has {len(valid_items)} items"
                        )
                    results = [self._process_result(r) for r in result]
                else:
                    # Single result for entire batch - replicate for each item
                    processed_result = self._process_result(result)
                    results = [processed_result] * len(valid_items)

                # Create records for each item in the batch
                for item_id, row_dict, item_result in zip(
                    batch_item_ids, batch_row_dicts, results
                ):
                    # Create flattened Record from Result
                    record = Record(
                        item_id=item_id,
                        dataset_row=row_dict,
                        prompt=item_result.prompt,
                        model_response=item_result.model_response,
                        scores=item_result.scores,
                        error=None,
                    )
                    session_manager.add_results([record])
                    progress_manager.update_evaluation_progress(
                        dataset_info.get("name", "dataset"), result=record
                    )

            except Exception as e:
                # Create error records for all items in the batch
                for item_id, row_dict in zip(batch_item_ids, batch_row_dicts):
                    error_record = self._create_error_record(item_id, row_dict, e)
                    session_manager.add_results([error_record])
                    progress_manager.update_evaluation_progress(
                        dataset_info.get("name", "dataset"), result=error_record
                    )

    async def _execute_async(
        self,
        eval_fn: Callable,
        columns: list[str],
        dataset_items: list[tuple[int, dict[str, Any] | Exception]],
        session_manager: SessionManager,
        progress_manager: BaseProgressManager,
        dataset_info: DatasetInfo,
        **kwargs: Any,
    ) -> None:
        """Execute asynchronous evaluation in batches."""
        batch_size = kwargs.pop("batch_size", None)

        total_items = len(dataset_items)

        progress_manager.start_evaluation(
            dataset_info.get("name", "dataset"), total_items, dataset_info
        )

        # Process items in batches
        for batch in _chunk_dataset(dataset_items, batch_size):
            # Separate valid items from error items
            error_items = [
                (item_id, data)
                for item_id, data in batch
                if isinstance(data, Exception)
            ]
            valid_items = [
                (item_id, data)
                for item_id, data in batch
                if not isinstance(data, Exception)
            ]

            # Process error items first
            for item_id, error in error_items:
                error_record = self._create_error_record(item_id, {}, error)
                session_manager.add_results([error_record])
                progress_manager.update_evaluation_progress(
                    dataset_info.get("name", "dataset"), result=error_record
                )

            # Skip batch if no valid items
            if not valid_items:
                continue

            batch_item_ids = [item_id for item_id, _ in valid_items]
            batch_row_dicts = [row_dict for _, row_dict in valid_items]

            # Prepare batch inputs (lists of values for each column)
            batch_inputs = {
                col: [row[col] for row in batch_row_dicts] for col in columns
            }

            try:
                # Run evaluation on the batch
                result = await eval_fn(**batch_inputs, **kwargs)

                # Handle both list of results and single result for entire batch
                if isinstance(result, list):
                    if len(result) != len(valid_items):
                        raise ValueError(
                            f"Batch function returned {len(result)} results but batch has {len(valid_items)} items"
                        )
                    results = [self._process_result(r) for r in result]
                else:
                    # Single result for entire batch - replicate for each item
                    processed_result = self._process_result(result)
                    results = [processed_result] * len(valid_items)

                # Create records for each item in the batch
                for item_id, row_dict, item_result in zip(
                    batch_item_ids, batch_row_dicts, results
                ):
                    # Create flattened Record from Result
                    record = Record(
                        item_id=item_id,
                        dataset_row=row_dict,
                        prompt=item_result.prompt,
                        model_response=item_result.model_response,
                        scores=item_result.scores,
                        error=None,
                    )
                    session_manager.add_results([record])
                    progress_manager.update_evaluation_progress(
                        dataset_info.get("name", "dataset"), result=record
                    )

            except Exception as e:
                # Create error records for all items in the batch
                for item_id, row_dict in zip(batch_item_ids, batch_row_dicts):
                    error_record = self._create_error_record(item_id, row_dict, e)
                    session_manager.add_results([error_record])
                    progress_manager.update_evaluation_progress(
                        dataset_info.get("name", "dataset"), result=error_record
                    )


# Register with the global registry
executor_registry.register("batch", BatchExecutor())
