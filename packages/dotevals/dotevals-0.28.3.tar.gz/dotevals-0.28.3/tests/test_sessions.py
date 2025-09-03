"""Simplified session management tests."""

import re
import time
from unittest.mock import patch

import pytest

from dotevals.results import EvaluationMetadata, EvaluationStatus, Record
from dotevals.sessions import SessionManager, get_git_commit


class TestSessionManager:
    """Core SessionManager tests."""

    def test_init_without_experiment(self, tmp_path):
        """Test initialization without experiment creates ephemeral."""
        import uuid

        eval_name = f"test_eval_{uuid.uuid4().hex[:8]}"
        manager = SessionManager(eval_name, storage=f"json://{tmp_path}")

        assert manager.storage is not None
        assert manager.current_experiment is not None
        # Should create timestamped ephemeral experiment
        assert re.match(r"\d{8}_\d{6}_[a-f0-9]{8}", manager.current_experiment)

    def test_init_with_experiment(self, tmp_path):
        """Test initialization with named experiment."""
        import uuid

        unique_id = uuid.uuid4().hex[:8]
        eval_name = f"test_eval_{unique_id}"
        exp_name = f"test_exp_{unique_id}"
        manager = SessionManager(
            evaluation_name=eval_name,
            experiment_name=exp_name,
            storage=f"json://{tmp_path}",
        )

        assert manager.current_experiment == exp_name
        assert manager.current_evaluation == eval_name
        assert exp_name in manager.storage.list_experiments()

    @patch("dotevals.sessions.get_git_commit")
    def test_start_evaluation(self, mock_git_commit, tmp_path):
        """Test starting an evaluation."""
        mock_git_commit.return_value = "abc123"

        import uuid

        unique_id = uuid.uuid4().hex[:8]
        manager = SessionManager(
            evaluation_name=f"eval1_{unique_id}",
            experiment_name=f"test_exp_{unique_id}",
            storage=f"json://{tmp_path}",
        )

        manager.start_evaluation()

        # Check evaluation was created
        evaluations = manager.storage.list_evaluations(manager.current_experiment)
        assert manager.current_evaluation in evaluations

        # Check evaluation status
        eval_obj = manager.storage.load_evaluation(
            manager.current_experiment, manager.current_evaluation
        )
        assert eval_obj.status == EvaluationStatus.RUNNING
        assert eval_obj.metadata.get("git_commit") == "abc123"

    def test_add_results(self, tmp_path):
        """Test adding results to evaluation."""
        import uuid

        unique_id = uuid.uuid4().hex[:8]
        manager = SessionManager(
            evaluation_name=f"eval1_{unique_id}",
            experiment_name=f"test_exp_{unique_id}",
            storage=f"json://{tmp_path}",
        )

        manager.start_evaluation()

        # Add results
        record = Record(
            item_id=0,
            dataset_row={"input": "test"},
            scores=[],
            prompt=None,
            model_response=None,
        )
        manager.add_results([record])

        # Verify results were stored
        results = manager.storage.get_results(
            manager.current_experiment, manager.current_evaluation
        )
        assert len(results) == 1
        assert results[0].dataset_row["input"] == "test"

    def test_finish_evaluation(self, tmp_path):
        """Test finishing an evaluation."""
        import uuid

        unique_id = uuid.uuid4().hex[:8]
        manager = SessionManager(
            evaluation_name=f"eval1_{unique_id}",
            experiment_name=f"test_exp_{unique_id}",
            storage=f"json://{tmp_path}",
        )

        manager.start_evaluation()
        manager.finish_evaluation()

        # Check status updated
        eval_obj = manager.storage.load_evaluation(
            manager.current_experiment, manager.current_evaluation
        )
        assert eval_obj.status == EvaluationStatus.COMPLETED

    def test_get_results(self, tmp_path):
        """Test retrieving results."""
        import uuid

        unique_id = uuid.uuid4().hex[:8]
        manager = SessionManager(
            evaluation_name=f"eval1_{unique_id}",
            experiment_name=f"test_exp_{unique_id}",
            storage=f"json://{tmp_path}",
        )

        manager.start_evaluation()

        # Add some results
        records = [
            Record(
                item_id=i,
                dataset_row={"idx": i},
                scores=[],
                prompt=None,
                model_response=None,
            )
            for i in range(5)
        ]
        manager.add_results(records)

        # Get results
        retrieved = manager.get_results()
        assert len(retrieved) == 5
        assert all(r.dataset_row["idx"] == i for i, r in enumerate(retrieved))

    def test_evaluation_progress_tracking(self, tmp_path):
        """Test progress tracking during evaluation."""
        import uuid

        unique_id = uuid.uuid4().hex[:8]
        manager = SessionManager(
            evaluation_name=f"eval1_{unique_id}",
            experiment_name=f"test_exp_{unique_id}",
            storage=f"json://{tmp_path}",
        )

        manager.start_evaluation()

        # Track progress manually since evaluation_progress is EvaluationProgress object
        completed = 0

        # Add results incrementally
        for i in range(5):
            record = Record(
                item_id=i,
                dataset_row={"idx": i},
                scores=[],
                prompt=None,
                model_response=None,
            )
            manager.add_results([record])
            completed += 1

        # Check through evaluation_progress object
        assert manager.evaluation_progress.completed_count == 5
        assert manager.evaluation_progress.error_count == 0

    def test_ephemeral_experiment_naming(self, tmp_path):
        """Test ephemeral experiment name generation."""
        import uuid
        from unittest.mock import Mock

        # Generate eval name before patching
        eval_name = f"test_eval_{uuid.uuid4().hex[:8]}"

        with patch("dotevals.sessions.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "20240101_120000"

            with patch("dotevals.sessions.uuid.uuid4") as mock_uuid4:
                mock_obj = Mock()
                # uuid4() returns object, then we convert to str and slice [:8]
                mock_obj.__str__ = Mock(
                    return_value="abcd1234-efgh-ijkl-mnop-qrstuvwxyz12"
                )
                mock_uuid4.return_value = mock_obj

                manager = SessionManager(eval_name, storage=f"json://{tmp_path}")

                assert manager.current_experiment == "20240101_120000_abcd1234"

    def test_no_storage_url(self, tmp_path):
        """Test initialization without storage URL uses default."""
        import uuid

        eval_name = f"test_eval_{uuid.uuid4().hex[:8]}"
        manager = SessionManager(eval_name, storage=f"json://{tmp_path}")

        # Should create storage
        assert manager.storage is not None

        # Should be able to use it normally
        manager.start_evaluation()
        manager.finish_evaluation()


class TestGitIntegration:
    """Tests for git integration."""

    def test_get_git_commit_success(self):
        """Test getting git commit when in repo."""
        with patch("subprocess.check_output") as mock_check:
            mock_check.return_value = b"abc123def456789\n"

            commit = get_git_commit()

            assert commit == "abc123de"
            mock_check.assert_called_once()

    def test_get_git_commit_not_repo(self):
        """Test getting git commit outside repo."""
        import subprocess

        with patch("subprocess.check_output") as mock_check:
            mock_check.side_effect = subprocess.CalledProcessError(128, "git")

            commit = get_git_commit()

            assert commit is None

    def test_get_git_commit_error(self):
        """Test git commit with subprocess error."""
        with patch("subprocess.check_output") as mock_check:
            mock_check.side_effect = Exception("Git not found")

            # get_git_commit doesn't catch generic exceptions, only CalledProcessError
            # So this will raise
            with pytest.raises(Exception):
                get_git_commit()


@pytest.mark.parametrize(
    "status",
    [
        EvaluationStatus.RUNNING,
        EvaluationStatus.COMPLETED,
        EvaluationStatus.FAILED,
    ],
)
def test_evaluation_status_transitions(tmp_path, status):
    """Test different evaluation status transitions."""
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    manager = SessionManager(
        evaluation_name=f"eval1_{unique_id}",
        experiment_name=f"test_exp_{unique_id}",
        storage=f"json://{tmp_path}",
    )

    manager.start_evaluation()

    # Update status
    manager.storage.update_evaluation_status(
        manager.current_experiment, manager.current_evaluation, status
    )

    # Verify
    eval_obj = manager.storage.load_evaluation(
        manager.current_experiment, manager.current_evaluation
    )
    assert eval_obj.status == status


def test_finish_evaluation_with_failure(tmp_path):
    """Test finishing evaluation with failure status."""
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    manager = SessionManager(
        evaluation_name=f"eval1_{unique_id}",
        experiment_name=f"test_exp_{unique_id}",
        storage=f"json://{tmp_path}",
    )

    manager.start_evaluation()
    manager.finish_evaluation(success=False)

    # Check status updated to FAILED
    eval_obj = manager.storage.load_evaluation(
        manager.current_experiment, manager.current_evaluation
    )
    assert eval_obj.status == EvaluationStatus.FAILED


def test_add_results_with_errors(tmp_path):
    """Test adding results with errors updates progress tracking."""
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    manager = SessionManager(
        evaluation_name=f"eval1_{unique_id}",
        experiment_name=f"test_exp_{unique_id}",
        storage=f"json://{tmp_path}",
    )

    manager.start_evaluation()

    # Add results with errors
    records = [
        Record(
            item_id=0,
            dataset_row={"idx": 0},
            scores=[],
            prompt=None,
            model_response=None,
            error="Error 1",
        ),
        Record(
            item_id=1,
            dataset_row={"idx": 1},
            scores=[],
            prompt=None,
            model_response=None,
        ),
        Record(
            item_id=2,
            dataset_row={"idx": 2},
            scores=[],
            prompt=None,
            model_response=None,
            error="Error 2",
        ),
    ]

    manager.add_results(records)

    # Check error tracking
    assert manager.evaluation_progress.completed_count == 3
    assert manager.evaluation_progress.error_count == 2


def test_session_without_start_evaluation(tmp_path):
    """Test adding results without calling start_evaluation."""
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    exp_name = f"test_exp_{unique_id}"
    eval_name = f"eval1_{unique_id}"
    manager = SessionManager(
        evaluation_name=eval_name,
        experiment_name=exp_name,
        storage=f"json://{tmp_path}",
    )

    # Don't call start_evaluation - evaluation_progress is None
    assert manager.evaluation_progress is None

    # Create evaluation manually so storage doesn't complain
    eval = EvaluationMetadata(
        evaluation_name=eval_name,
        started_at=time.time(),
        status=EvaluationStatus.RUNNING,
    )
    manager.storage.create_evaluation(exp_name, eval)

    # Should handle gracefully without evaluation_progress
    record = Record(
        item_id=0,
        dataset_row={"test": "data"},
        scores=[],
        prompt=None,
        model_response=None,
        error="Error",
    )

    # This should not crash even though evaluation_progress is None
    manager.add_results([record])

    # Results should still be stored
    results = manager.storage.get_results(exp_name, eval_name)
    assert len(results) == 1


def test_resume_evaluation_with_existing_results(tmp_path):
    """Test resuming an evaluation that already has results."""
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    exp_name = f"test_exp_{unique_id}"
    eval_name = f"eval1_{unique_id}"

    # First session
    manager1 = SessionManager(
        evaluation_name=eval_name,
        experiment_name=exp_name,
        storage=f"json://{tmp_path}",
    )
    manager1.start_evaluation()

    records = [
        Record(
            item_id=i,
            dataset_row={"idx": i},
            scores=[],
            prompt=None,
            model_response=None,
        )
        for i in range(5)
    ]
    manager1.add_results(records)
    # Don't finish - simulate crash

    # Second session resumes
    manager2 = SessionManager(
        evaluation_name=eval_name,
        experiment_name=exp_name,
        storage=f"json://{tmp_path}",
    )

    # Should detect existing evaluation (prints message)
    import io
    import sys

    captured = io.StringIO()
    sys.stdout = captured
    manager2.start_evaluation()
    sys.stdout = sys.__stdout__

    output = captured.getvalue()
    assert "Resuming from 5 completed samples" in output

    # Add more results
    more_records = [
        Record(
            item_id=i,
            dataset_row={"idx": i},
            scores=[],
            prompt=None,
            model_response=None,
        )
        for i in range(5, 10)
    ]
    manager2.add_results(more_records)

    # All results present
    final_results = manager2.get_results()
    assert len(final_results) == 10


def test_concurrent_result_addition(tmp_path):
    """Test adding results concurrently."""
    import threading
    import uuid

    unique_id = uuid.uuid4().hex[:8]
    manager = SessionManager(
        evaluation_name=f"eval1_{unique_id}",
        experiment_name=f"test_exp_{unique_id}",
        storage=f"json://{tmp_path}",
    )

    manager.start_evaluation()

    def add_batch(start_idx):
        """Add a batch of results."""
        records = [
            Record(
                item_id=start_idx + i,
                dataset_row={"idx": start_idx + i},
                scores=[],
                prompt=None,
                model_response=None,
            )
            for i in range(10)
        ]
        manager.add_results(records)

    # Start multiple threads
    threads = []
    for i in range(0, 50, 10):
        t = threading.Thread(target=add_batch, args=(i,))
        threads.append(t)
        t.start()

    # Wait for completion
    for t in threads:
        t.join()

    # Verify all results
    results = manager.get_results()
    assert len(results) == 50
    item_ids = [r.item_id for r in results]
    assert sorted(item_ids) == list(range(50))
