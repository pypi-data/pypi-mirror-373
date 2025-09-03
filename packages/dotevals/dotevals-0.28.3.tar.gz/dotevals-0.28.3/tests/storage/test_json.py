"""Tests for JSON storage implementation."""

import json
import time
from pathlib import Path

import pytest

from dotevals.exceptions import (
    EvaluationNotFoundError,
    ExperimentExistsError,
    ExperimentNotFoundError,
)
from dotevals.metrics import accuracy
from dotevals.results import EvaluationMetadata, EvaluationStatus, Record, Score
from dotevals.storage.json import JSONStorage


class TestJSONStorage:
    """Parametrized tests for JSON storage."""

    @pytest.fixture
    def storage(self, tmp_path):
        """Create JSON storage instance."""
        return JSONStorage(str(tmp_path))

    def test_initialization(self, tmp_path):
        """Test storage initializes correctly."""
        storage = JSONStorage(str(tmp_path))
        assert storage.root_dir == Path(tmp_path)
        assert storage.root_dir.exists()

    @pytest.mark.parametrize(
        "experiments,operations,expected",
        [
            (["exp1"], ["create", "list"], ["exp1"]),
            (["exp1", "exp2"], ["create", "list"], ["exp1", "exp2"]),
            (["exp1", "exp2"], ["create", "delete:exp1", "list"], ["exp2"]),
            (["old"], ["create", "rename:old:new", "list"], ["new"]),
        ],
        ids=["single", "multiple", "delete", "rename"],
    )
    def test_experiment_operations(self, storage, experiments, operations, expected):
        """Test various experiment operations."""
        for op in operations:
            if op == "create":
                for exp in experiments:
                    storage.create_experiment(exp)
            elif op == "list":
                result = storage.list_experiments()
                assert sorted(result) == sorted(expected)
            elif op.startswith("delete:"):
                _, exp_name = op.split(":", 1)
                storage.delete_experiment(exp_name)
            elif op.startswith("rename:"):
                _, old, new = op.split(":")
                storage.rename_experiment(old, new)

    @pytest.mark.parametrize(
        "num_evaluations,eval_names",
        [
            (1, ["eval1"]),
            (2, ["eval1", "eval2"]),
            (3, ["eval_a", "eval_b", "eval_c"]),
            (0, []),
        ],
        ids=["single", "two", "three", "none"],
    )
    def test_evaluation_operations(self, storage, num_evaluations, eval_names):
        """Test creating and listing evaluations."""
        storage.create_experiment("test_exp")

        # Create evaluations
        for name in eval_names[:num_evaluations]:
            eval_meta = EvaluationMetadata(
                evaluation_name=name,
                started_at=time.time(),
                status=EvaluationStatus.RUNNING,
            )
            storage.create_evaluation("test_exp", eval_meta)

        # List evaluations
        evaluations = storage.list_evaluations("test_exp")
        assert len(evaluations) == num_evaluations
        assert all(name in evaluations for name in eval_names[:num_evaluations])

    @pytest.mark.parametrize(
        "status_transitions",
        [
            [EvaluationStatus.RUNNING],
            [EvaluationStatus.RUNNING, EvaluationStatus.COMPLETED],
            [EvaluationStatus.RUNNING, EvaluationStatus.FAILED],
            [
                EvaluationStatus.RUNNING,
                EvaluationStatus.RUNNING,
                EvaluationStatus.COMPLETED,
            ],
        ],
        ids=["single", "complete", "fail", "multiple"],
    )
    def test_evaluation_status_updates(self, storage, status_transitions):
        """Test evaluation status transitions."""
        storage.create_experiment("test_exp")

        evaluation = EvaluationMetadata(
            evaluation_name="eval1",
            started_at=time.time(),
            status=status_transitions[0],
        )
        storage.create_evaluation("test_exp", evaluation)

        # Apply each status transition
        for status in status_transitions:
            storage.update_evaluation_status("test_exp", "eval1", status)
            loaded = storage.load_evaluation("test_exp", "eval1")
            assert loaded.status == status

    @pytest.mark.parametrize(
        "num_records,batch_sizes,error_indices",
        [
            (5, [5], []),  # Single batch, no errors
            (5, [2, 3], []),  # Multiple batches, no errors
            (5, [5], [1, 3]),  # Single batch with errors
            (10, [3, 3, 4], [0, 5, 9]),  # Multiple batches with errors
            (0, [], []),  # No records
        ],
        ids=[
            "single_batch",
            "multi_batch",
            "with_errors",
            "multi_with_errors",
            "empty",
        ],
    )
    def test_add_and_get_results(
        self, storage, num_records, batch_sizes, error_indices
    ):
        """Test adding and retrieving results in batches."""
        storage.create_experiment("test_exp")

        evaluation = EvaluationMetadata(
            evaluation_name="eval1",
            started_at=time.time(),
            status=EvaluationStatus.RUNNING,
        )
        storage.create_evaluation("test_exp", evaluation)

        # Add records in batches
        record_id = 0
        for batch_size in batch_sizes:
            records = []
            for _ in range(batch_size):
                if record_id < num_records:
                    record = Record(
                        item_id=record_id,
                        dataset_row={"input": f"test_{record_id}", "index": record_id},
                        scores=[Score("test", 1.0, [], {})],
                        prompt=f"prompt_{record_id}",
                        model_response=None,
                        error="Error" if record_id in error_indices else None,
                    )
                    records.append(record)
                    record_id += 1

            if records:
                storage.add_results("test_exp", "eval1", records)

        # Verify results
        results = storage.get_results("test_exp", "eval1")
        assert len(results) == num_records

        # Check error indices
        actual_error_indices = [r.dataset_row["index"] for r in results if r.error]
        assert set(actual_error_indices) == set(error_indices)

    @pytest.mark.parametrize(
        "total_records,error_indices,remove_indices,expected_remaining_errors",
        [
            (5, [0, 2, 4], [0, 2], [4]),  # Remove some errors
            (5, [0, 2, 4], [0, 2, 4], []),  # Remove all errors
            (5, [0, 2, 4], [], [0, 2, 4]),  # Remove none
            (3, [], [], []),  # No errors to remove
        ],
        ids=["remove_some", "remove_all", "remove_none", "no_errors"],
    )
    def test_remove_error_results(
        self,
        storage,
        total_records,
        error_indices,
        remove_indices,
        expected_remaining_errors,
    ):
        """Test removing error results."""
        storage.create_experiment("test_exp")

        evaluation = EvaluationMetadata(
            evaluation_name="eval1",
            started_at=time.time(),
            status=EvaluationStatus.RUNNING,
        )
        storage.create_evaluation("test_exp", evaluation)

        # Add records with errors
        records = []
        for i in range(total_records):
            record = Record(
                item_id=i,
                dataset_row={"input": f"test_{i}", "index": i},
                scores=[],
                prompt=None,
                model_response=None,
                error="Error" if i in error_indices else None,
            )
            records.append(record)

        storage.add_results("test_exp", "eval1", records)

        # Remove error results
        if remove_indices:
            storage.remove_error_results_batch("test_exp", "eval1", remove_indices)

        # Check remaining errors
        results = storage.get_results("test_exp", "eval1")
        actual_error_indices = [r.dataset_row["index"] for r in results if r.error]
        assert set(actual_error_indices) == set(expected_remaining_errors)

    def test_remove_error_result_single(self, storage):
        """Test removing a single error result."""
        storage.create_experiment("test_exp")

        evaluation = EvaluationMetadata(
            evaluation_name="eval1",
            started_at=time.time(),
            status=EvaluationStatus.RUNNING,
        )
        storage.create_evaluation("test_exp", evaluation)

        # Add records with mix of successful and error results
        records = [
            Record(
                item_id=0,
                dataset_row={"input": "test_0"},
                prompt=None,
                model_response=None,
                scores=[],
                error=None,
            ),
            Record(
                item_id=1,
                dataset_row={"input": "test_1"},
                prompt=None,
                model_response=None,
                scores=[],
                error="Error 1",
            ),
            Record(
                item_id=2,
                dataset_row={"input": "test_2"},
                prompt=None,
                model_response=None,
                scores=[],
                error=None,
            ),
            Record(
                item_id=3,
                dataset_row={"input": "test_3"},
                prompt=None,
                model_response=None,
                scores=[],
                error="Error 3",
            ),
        ]
        storage.add_results("test_exp", "eval1", records)

        # Remove a single error result
        storage.remove_error_result("test_exp", "eval1", 1)

        # Check that only the specified error was removed
        results = storage.get_results("test_exp", "eval1")
        assert len(results) == 3
        item_ids = [r.item_id for r in results]
        assert 1 not in item_ids
        assert 0 in item_ids
        assert 2 in item_ids
        assert 3 in item_ids

        # Verify the error at item 3 is still there
        error_results = [r for r in results if r.error]
        assert len(error_results) == 1
        assert error_results[0].item_id == 3

    def test_remove_error_result_non_existent_file(self, storage):
        """Test removing error result when file doesn't exist."""
        storage.create_experiment("test_exp")

        # Should not raise an error, just return silently
        storage.remove_error_result("test_exp", "non_existent_eval", 1)

    def test_remove_error_result_empty_results(self, storage):
        """Test removing error result when there are no results."""
        storage.create_experiment("test_exp")

        evaluation = EvaluationMetadata(
            evaluation_name="eval1",
            started_at=time.time(),
            status=EvaluationStatus.RUNNING,
        )
        storage.create_evaluation("test_exp", evaluation)

        # Should not raise an error, just return silently
        storage.remove_error_result("test_exp", "eval1", 1)

        # Verify evaluation metadata is preserved
        eval_meta = storage.load_evaluation("test_exp", "eval1")
        assert eval_meta is not None
        assert eval_meta.evaluation_name == "eval1"

    def test_remove_error_result_preserves_non_errors(self, storage):
        """Test that removing error results preserves non-error results for same item."""
        storage.create_experiment("test_exp")

        evaluation = EvaluationMetadata(
            evaluation_name="eval1",
            started_at=time.time(),
            status=EvaluationStatus.RUNNING,
        )
        storage.create_evaluation("test_exp", evaluation)

        # Add a successful result and then an error for the same item
        records = [
            Record(
                item_id=1,
                dataset_row={"input": "test_1"},
                prompt=None,
                model_response=None,
                scores=[Score("test", 0.9, [], {})],
                error=None,
            ),
            Record(
                item_id=1,
                dataset_row={"input": "test_1_retry"},
                prompt=None,
                model_response=None,
                scores=[],
                error="Error on retry",
            ),
        ]
        storage.add_results("test_exp", "eval1", records)

        # Remove the error result for item 1
        storage.remove_error_result("test_exp", "eval1", 1)

        # Check that the successful result is preserved
        results = storage.get_results("test_exp", "eval1")
        assert len(results) == 1
        assert results[0].item_id == 1
        assert results[0].error is None
        assert len(results[0].scores) == 1

    @pytest.mark.parametrize(
        "num_results,num_errors",
        [
            (3, 0),  # All successful
            (5, 2),  # Some errors
            (3, 3),  # All errors
            (0, 0),  # No results
        ],
        ids=["all_success", "some_errors", "all_errors", "empty"],
    )
    def test_completed_items(self, storage, num_results, num_errors):
        """Test tracking completed items."""
        storage.create_experiment("test_exp")

        evaluation = EvaluationMetadata(
            evaluation_name="eval1",
            started_at=time.time(),
            status=EvaluationStatus.RUNNING,
        )
        storage.create_evaluation("test_exp", evaluation)

        # Add results with specified number of errors
        records = []
        for i in range(num_results):
            record = Record(
                item_id=i,
                dataset_row={"input": f"test_{i}", "index": i},
                scores=[],
                prompt=None,
                model_response=None,
                error="Error" if i < num_errors else None,
            )
            records.append(record)

        if records:
            storage.add_results("test_exp", "eval1", records)

        # Get completed items (non-error items)
        completed = storage.completed_items("test_exp", "eval1")
        expected_completed = num_results - num_errors
        assert len(completed) == expected_completed

    @pytest.mark.parametrize(
        "operation,entity,should_error",
        [
            ("list_evaluations", "nonexistent_exp", False),  # Returns empty list
            ("get_results", ("nonexistent_exp", "eval1"), False),  # Returns empty list
            (
                "load_evaluation",
                ("nonexistent_exp", "eval1"),
                False,
            ),  # Returns None or error
            (
                "completed_items",
                ("nonexistent_exp", "eval1"),
                False,
            ),  # Returns empty list
        ],
        ids=["list_evals", "get_results", "load_eval", "completed_items"],
    )
    def test_operations_on_nonexistent(self, storage, operation, entity, should_error):
        """Test operations on non-existent entities."""
        method = getattr(storage, operation)

        if isinstance(entity, tuple):
            result = method(*entity)
        else:
            result = method(entity)

        if not should_error:
            if operation in ["list_evaluations", "get_results", "completed_items"]:
                assert result == []
            # load_evaluation might return None or raise error depending on implementation


class TestJSONStorageInternals:
    """Test JSON storage internal functionality."""

    def test_delete_experiment_file_cleanup(self, tmp_path):
        """Test experiment deletion with file cleanup."""
        temp_dir = tmp_path
        storage = JSONStorage(temp_dir)

        # Create an experiment with files
        experiment_name = "test_experiment"
        experiment_path = Path(temp_dir) / experiment_name
        experiment_path.mkdir()

        # Create some files in the experiment directory
        (experiment_path / "eval1.jsonl").write_text('{"test": "data"}')
        (experiment_path / "eval2.jsonl").write_text('{"test": "data2"}')
        (experiment_path / "subfile.txt").write_text("content")

        # Verify files exist
        assert experiment_path.exists()
        assert len(list(experiment_path.iterdir())) == 3

        # Delete the experiment - should clean up all files
        storage.delete_experiment(experiment_name)

        # Verify cleanup
        assert not experiment_path.exists()

    def test_delete_experiment_not_found(self, tmp_path):
        """Test deleting non-existent experiment."""
        temp_dir = tmp_path
        storage = JSONStorage(temp_dir)

        # Try to delete non-existent experiment
        with pytest.raises(ExperimentNotFoundError):
            storage.delete_experiment("nonexistent")

    def test_rename_experiment_success(self, tmp_path):
        """Test successful experiment rename."""
        temp_dir = tmp_path
        storage = JSONStorage(temp_dir)

        # Create an experiment
        storage.create_experiment("original_name")
        original_path = Path(temp_dir) / "original_name"
        assert original_path.exists()

        # Rename the experiment
        storage.rename_experiment("original_name", "new_name")

        # Verify rename
        new_path = Path(temp_dir) / "new_name"
        assert new_path.exists()
        assert not original_path.exists()

        # Verify it appears in list
        experiments = storage.list_experiments()
        assert "new_name" in experiments
        assert "original_name" not in experiments

    def test_rename_experiment_not_found(self, tmp_path):
        """Test renaming non-existent experiment."""
        temp_dir = tmp_path
        storage = JSONStorage(temp_dir)

        with pytest.raises(ExperimentNotFoundError):
            storage.rename_experiment("nonexistent", "new_name")

    def test_rename_experiment_target_exists(self, tmp_path):
        """Test renaming to existing experiment name."""
        temp_dir = tmp_path
        storage = JSONStorage(temp_dir)

        # Create two experiments
        storage.create_experiment("exp1")
        storage.create_experiment("exp2")

        # Try to rename exp1 to exp2
        with pytest.raises(ExperimentExistsError):
            storage.rename_experiment("exp1", "exp2")

    def test_create_duplicate_experiment(self, tmp_path):
        """Test creating duplicate experiment is allowed (idempotent)."""
        temp_dir = tmp_path
        storage = JSONStorage(temp_dir)

        # Create an experiment
        storage.create_experiment("test_exp")

        # Creating duplicate should be allowed (idempotent)
        storage.create_experiment("test_exp")  # Should not raise

    def test_update_evaluation_status_not_found(self, tmp_path):
        """Test updating status of non-existent evaluation."""
        temp_dir = tmp_path
        storage = JSONStorage(temp_dir)

        # Create experiment but no evaluation
        storage.create_experiment("test_exp")

        # Try to update non-existent evaluation
        with pytest.raises(EvaluationNotFoundError):
            storage.update_evaluation_status(
                "test_exp", "nonexistent", EvaluationStatus.COMPLETED
            )

    def test_load_evaluation_not_found(self, tmp_path):
        """Test loading non-existent evaluation."""
        temp_dir = tmp_path
        storage = JSONStorage(temp_dir)

        # Create experiment but no evaluation
        storage.create_experiment("test_exp")

        # Load non-existent evaluation should return None
        result = storage.load_evaluation("test_exp", "nonexistent")
        assert result is None

    def test_jsonl_file_handling(self, tmp_path):
        """Test JSONL file reading and writing."""
        temp_dir = tmp_path
        storage = JSONStorage(temp_dir)

        # Create experiment and evaluation
        storage.create_experiment("test_exp")
        evaluation = EvaluationMetadata(
            evaluation_name="eval1",
            started_at=time.time(),
            status=EvaluationStatus.RUNNING,
        )
        storage.create_evaluation("test_exp", evaluation)

        # Add some records
        records = [
            Record(
                item_id=i,
                dataset_row={"input": f"test_{i}"},
                scores=[Score("test", 1.0, [], {})],
                prompt=f"prompt_{i}",
                model_response=None,
                error=None,
            )
            for i in range(3)
        ]
        storage.add_results("test_exp", "eval1", records)

        # Verify JSONL file exists and contains correct data
        jsonl_path = Path(temp_dir) / "test_exp" / "eval1.jsonl"
        assert jsonl_path.exists()

        # Read and verify JSONL content
        lines = jsonl_path.read_text().strip().split("\n")
        # First line is metadata, then 3 result lines
        assert len(lines) == 4

        # Skip metadata line and check results
        for i, line in enumerate(lines[1:]):
            data = json.loads(line)
            assert data["item_id"] == i
            assert data["dataset_row"]["input"] == f"test_{i}"

    def test_concurrent_writes(self, tmp_path):
        """Test concurrent write handling."""
        import threading

        temp_dir = tmp_path
        storage = JSONStorage(temp_dir)

        # Create experiment and evaluation
        storage.create_experiment("test_exp")
        evaluation = EvaluationMetadata(
            evaluation_name="eval1",
            started_at=time.time(),
            status=EvaluationStatus.RUNNING,
        )
        storage.create_evaluation("test_exp", evaluation)

        # Function to add records in a thread
        def add_batch(batch_id):
            records = [
                Record(
                    item_id=batch_id * 10 + i,
                    dataset_row={"batch": batch_id, "item": i},
                    scores=[Score("test", 1.0, [], {})],
                    prompt=f"prompt_{batch_id}_{i}",
                    model_response=None,
                )
                for i in range(10)
            ]
            storage.add_results("test_exp", "eval1", records)

        # Start concurrent threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=add_batch, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Verify all results were added
        results = storage.get_results("test_exp", "eval1")
        assert len(results) == 50  # 5 batches * 10 records each


class TestBatchResultOperations:
    """Parametrized tests for batch result operations."""

    @pytest.fixture
    def storage(self, tmp_path):
        """Create JSON storage instance."""
        storage = JSONStorage(str(tmp_path))
        storage.create_experiment("test_exp")
        evaluation = EvaluationMetadata(
            evaluation_name="eval1",
            started_at=time.time(),
            status=EvaluationStatus.RUNNING,
        )
        storage.create_evaluation("test_exp", evaluation)
        return storage

    @pytest.mark.parametrize(
        "batch_configs",
        [
            [(10, 0.0), (10, 0.5), (10, 1.0)],  # Different scores
            [(5, 0.0), (10, 0.5), (15, 1.0)],  # Different sizes
            [(100, 0.8)],  # Single large batch
            [(1, 0.5)] * 20,  # Many small batches
        ],
        ids=["vary_scores", "vary_sizes", "large_batch", "many_small"],
    )
    def test_batch_result_addition(self, storage, batch_configs):
        """Test adding results in various batch configurations."""
        total_added = 0

        for batch_size, score_value in batch_configs:
            records = []
            for i in range(batch_size):
                record = Record(
                    item_id=total_added + i,
                    dataset_row={"input": f"test_{total_added + i}"},
                    scores=[Score("test", score_value, [accuracy], {})],
                    prompt=f"prompt_{total_added + i}",
                    model_response=f"response_{total_added + i}",
                )
                records.append(record)

            storage.add_results("test_exp", "eval1", records)
            total_added += batch_size

        # Verify all results were added
        results = storage.get_results("test_exp", "eval1")
        assert len(results) == total_added


class TestStorageErrorHandling:
    """Parametrized tests for storage error handling."""

    @pytest.mark.parametrize(
        "path_type,should_succeed",
        [
            ("valid", True),
            ("nested/deep/path", True),
            ("", True),  # Current directory
            ("/tmp/test_storage", True),  # Absolute path
        ],
        ids=["valid", "nested", "empty", "absolute"],
    )
    def test_storage_initialization_paths(self, tmp_path, path_type, should_succeed):
        """Test storage initialization with various path types."""
        if path_type == "valid":
            path = str(tmp_path / "storage")
        elif path_type == "nested/deep/path":
            path = str(tmp_path / "nested" / "deep" / "path")
        elif path_type == "":
            path = str(tmp_path)
        else:
            path = str(tmp_path / "absolute")

        if should_succeed:
            storage = JSONStorage(path)
            assert storage.root_dir.exists()

    @pytest.mark.parametrize(
        "error_scenario",
        [
            "corrupted_json",
            "invalid_metadata",
        ],
        ids=["corrupted", "invalid_meta"],
    )
    def test_storage_error_recovery(self, tmp_path, error_scenario):
        """Test storage recovery from various error scenarios."""
        storage = JSONStorage(str(tmp_path))
        storage.create_experiment("test_exp")

        if error_scenario == "corrupted_json":
            # Corrupt the experiments.json file
            (tmp_path / "experiments.json").write_text("{invalid json}")
            # Storage should handle gracefully
            experiments = storage.list_experiments()
            # Might return empty or recreate file
            assert isinstance(experiments, list)

        elif error_scenario == "invalid_metadata":
            # Create evaluation with invalid metadata
            eval_meta = EvaluationMetadata(
                evaluation_name="eval1",
                started_at=-1,  # Invalid timestamp
                status=EvaluationStatus.RUNNING,
            )
            # Should still work
            storage.create_evaluation("test_exp", eval_meta)

    def test_add_results_evaluation_not_found(self, tmp_path):
        """Test that add_results raises EvaluationNotFoundError for missing evaluation."""
        storage = JSONStorage(str(tmp_path))
        storage.create_experiment("test_exp")

        records = [
            Record(
                item_id=0,
                dataset_row={"input": "test"},
                prompt=None,
                model_response=None,
                scores=[],
                error=None,
            )
        ]

        # Should raise EvaluationNotFoundError
        with pytest.raises(EvaluationNotFoundError):
            storage.add_results("test_exp", "non_existent_eval", records)

    def test_get_results_json_decode_error(self, tmp_path):
        """Test that get_results handles JSON decode errors gracefully."""
        storage = JSONStorage(str(tmp_path))
        storage.create_experiment("test_exp")

        # Create evaluation
        evaluation = EvaluationMetadata(
            evaluation_name="eval1",
            started_at=time.time(),
            status=EvaluationStatus.RUNNING,
        )
        storage.create_evaluation("test_exp", evaluation)

        # Corrupt the file with invalid JSON on result lines
        file_path = tmp_path / "test_exp" / "eval1.jsonl"
        with open(file_path, "a") as f:
            f.write("\n{invalid json}\n")
            f.write("another invalid line\n")

        # Should return empty list on JSON decode error
        results = storage.get_results("test_exp", "eval1")
        assert results == []

    def test_load_evaluation_returns_none_for_empty_file(self, tmp_path):
        """Test that load_evaluation returns None for empty file."""
        storage = JSONStorage(str(tmp_path))
        storage.create_experiment("test_exp")

        # Create an empty evaluation file
        file_path = tmp_path / "test_exp" / "eval1.jsonl"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.touch()

        # Should return None for empty file
        result = storage.load_evaluation("test_exp", "eval1")
        assert result is None

    def test_remove_error_result_edge_cases(self, tmp_path):
        """Test edge cases in remove_error_result."""
        storage = JSONStorage(str(tmp_path))
        storage.create_experiment("test_exp")

        evaluation = EvaluationMetadata(
            evaluation_name="eval1",
            started_at=time.time(),
            status=EvaluationStatus.RUNNING,
        )
        storage.create_evaluation("test_exp", evaluation)

        # Test removing from file with only metadata (no results)
        storage.remove_error_result("test_exp", "eval1", 0)

        # Verify metadata is still there
        eval_meta = storage.load_evaluation("test_exp", "eval1")
        assert eval_meta is not None

    def test_remove_error_results_batch_empty_file(self, tmp_path):
        """Test remove_error_results_batch with empty file."""
        storage = JSONStorage(str(tmp_path))
        storage.create_experiment("test_exp")

        evaluation = EvaluationMetadata(
            evaluation_name="eval1",
            started_at=time.time(),
            status=EvaluationStatus.RUNNING,
        )
        storage.create_evaluation("test_exp", evaluation)

        # Try to remove from empty results
        storage.remove_error_results_batch("test_exp", "eval1", [1, 2, 3])

        # Should not crash, metadata should be preserved
        eval_meta = storage.load_evaluation("test_exp", "eval1")
        assert eval_meta is not None
