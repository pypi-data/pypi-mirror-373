"""ForEach executor implementation."""

from collections.abc import Callable
from typing import Any

from dotevals.executors.base import DatasetInfo, Executor
from dotevals.executors.registry import executor_registry
from dotevals.progress import BaseProgressManager
from dotevals.results import Record
from dotevals.sessions import SessionManager


class ForEachExecutor(Executor):
    """Default ForEach executor plugin."""

    @property
    def name(self) -> str:
        return "foreach"

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
        """Execute synchronous evaluation for each item."""

        total_items = len(dataset_items)
        progress_manager.start_evaluation(
            dataset_info.get("name", "dataset"), total_items, dataset_info
        )

        # Execute items sequentially
        for item_id, row_data in dataset_items:
            if isinstance(row_data, Exception):
                result = self._create_error_record(item_id, {}, row_data)
            else:
                try:
                    eval_result = eval_fn(**row_data, **kwargs)

                    # Process the result
                    eval_result = self._process_result(eval_result)
                    # Create flattened Record from Result
                    result = Record(
                        item_id=item_id,
                        dataset_row=row_data,
                        prompt=eval_result.prompt,
                        model_response=eval_result.model_response,
                        scores=eval_result.scores,
                        error=None,
                    )
                except Exception as e:
                    # Convert exceptions to error records
                    result = self._create_error_record(item_id, row_data, e)

            session_manager.add_results([result])
            progress_manager.update_evaluation_progress(
                dataset_info.get("name", "dataset"), result=result
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
        """Execute asynchronous evaluation for each item."""

        total_items = len(dataset_items)
        progress_manager.start_evaluation(
            dataset_info.get("name", "dataset"), total_items, dataset_info
        )

        # Execute items sequentially
        for item_id, row_data in dataset_items:
            if isinstance(row_data, Exception):
                result = self._create_error_record(item_id, {}, row_data)
            else:
                try:
                    eval_result = await eval_fn(**row_data, **kwargs)

                    # Process the result
                    eval_result = self._process_result(eval_result)
                    # Create flattened Record from Result
                    result = Record(
                        item_id=item_id,
                        dataset_row=row_data,
                        prompt=eval_result.prompt,
                        model_response=eval_result.model_response,
                        scores=eval_result.scores,
                        error=None,
                    )
                except Exception as e:
                    # Convert exceptions to error records
                    result = self._create_error_record(item_id, row_data, e)

            session_manager.add_results([result])
            progress_manager.update_evaluation_progress(
                dataset_info.get("name", "dataset"), result=result
            )


# Register with the global registry
executor_registry.register("foreach", ForEachExecutor())
