"""Comprehensive CLI tests combining real implementations and targeted mocking.

Tests are organized by functionality:
- Real implementation tests for integration testing
- Mocked tests only where necessary for formatting, error simulation, etc.
"""

import tempfile
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from dotevals.cli import cli
from dotevals.datasets import Dataset
from dotevals.datasets import registry as dataset_registry
from dotevals.metrics import accuracy
from dotevals.results import EvaluationMetadata, EvaluationStatus, Record, Score
from dotevals.storage import registry as storage_registry
from dotevals.storage.base import Storage
from dotevals.storage.json import JSONStorage


class TestCLICommands:
    """Test CLI commands with real implementations."""

    @pytest.fixture(autouse=True)
    def clean_registries(self):
        """Clean up registries before and after each test."""
        # Store original registries
        original_storage = storage_registry._backends.copy()
        original_datasets = dataset_registry._dataset_classes.copy()
        original_discovery = dataset_registry._discovery_completed

        yield

        # Restore original registries
        storage_registry._backends = original_storage
        dataset_registry._dataset_classes = original_datasets
        dataset_registry._discovery_completed = original_discovery

    def test_list_command(self, tmp_path):
        """Test list command with real JSON storage backend."""
        tmpdir = tmp_path
        # Create real storage and data
        storage = JSONStorage(tmpdir)
        storage.create_experiment("real_project")
        storage.create_experiment("another_project")
        storage.create_experiment("20240101_120000_abcd1234")  # ephemeral
        storage.create_experiment(".dotevals")  # Should be skipped

        # Add evaluations with real data
        eval1 = EvaluationMetadata(
            evaluation_name="real_eval",
            started_at=1234567890.0,
            status=EvaluationStatus.COMPLETED,
        )
        storage.create_evaluation("real_project", eval1)

        # Use the actual CLI
        runner = CliRunner()
        result = runner.invoke(cli, ["list", "--storage", f"json://{tmpdir}"])

        # Verify output contains our experiments
        assert result.exit_code == 0
        assert "real_project" in result.output
        assert "another_project" in result.output
        # Check for ephemeral experiments section
        assert (
            "20240101_120000_abcd1234" in result.output or "Ephemeral" in result.output
        )

        # Test with name filter
        result = runner.invoke(
            cli, ["list", "--name", "real", "--storage", f"json://{tmpdir}"]
        )
        assert result.exit_code == 0
        assert "real_project" in result.output
        assert "another_project" not in result.output

        # Test empty storage
        with tempfile.TemporaryDirectory() as empty_dir:
            result = runner.invoke(cli, ["list", "--storage", f"json://{empty_dir}"])
            assert result.exit_code == 0
            assert "No experiments found" in result.output

    def test_show_command(self, tmp_path):
        """Test show command with real storage and evaluation data."""
        tmpdir = tmp_path
        storage = JSONStorage(tmpdir)
        storage.create_experiment("test_exp")

        # Create real evaluation
        evaluation = EvaluationMetadata(
            evaluation_name="test_eval",
            started_at=1234567890.0,
            status=EvaluationStatus.COMPLETED,
            metadata={"model": "test-model", "temperature": 0.5},
        )
        storage.create_evaluation("test_exp", evaluation)

        # Add real results
        records = [
            Record(
                item_id=0,
                dataset_row={"input": "2+2", "expected": "4", "actual": "4"},
                scores=[Score("exact_match", True, [accuracy()], {})],
                prompt="Test prompt 1",
                model_response=None,
            ),
            Record(
                item_id=1,
                dataset_row={"input": "3+3", "expected": "6", "actual": "5"},
                scores=[Score("exact_match", False, [accuracy()], {})],
                prompt="Test prompt 2",
                model_response=None,
            ),
            Record(
                item_id=2,
                dataset_row={"input": "4+4", "expected": "8", "actual": "8"},
                scores=[Score("exact_match", True, [accuracy()], {})],
                prompt="Test prompt 3",
                model_response=None,
                error="Connection timeout",
            ),
        ]
        storage.add_results("test_exp", "test_eval", records)

        runner = CliRunner()

        # Test summary view
        result = runner.invoke(
            cli, ["show", "test_exp", "--storage", f"json://{tmpdir}"]
        )
        assert result.exit_code == 0
        assert "test_eval" in result.output
        assert "exact_match" in result.output
        assert "accuracy" in result.output

        # Test full JSON output
        result = runner.invoke(
            cli, ["show", "test_exp", "--full", "--storage", f"json://{tmpdir}"]
        )
        assert result.exit_code == 0
        # Should contain JSON data
        assert '"prompt"' in result.output
        assert '"scores"' in result.output

        # Test error details
        result = runner.invoke(
            cli, ["show", "test_exp", "--errors", "--storage", f"json://{tmpdir}"]
        )
        assert result.exit_code == 0
        assert "Connection timeout" in result.output

        # Test specific evaluation
        result = runner.invoke(
            cli,
            [
                "show",
                "test_exp",
                "--evaluation",
                "test_eval",
                "--storage",
                f"json://{tmpdir}",
            ],
        )
        assert result.exit_code == 0
        assert "test_eval" in result.output

        # Test non-existent evaluation
        result = runner.invoke(
            cli,
            [
                "show",
                "test_exp",
                "--evaluation",
                "nonexistent",
                "--storage",
                f"json://{tmpdir}",
            ],
        )
        assert result.exit_code == 0
        assert "not found" in result.output.lower()

        # Test experiment with no evaluations
        storage.create_experiment("empty_exp")
        result = runner.invoke(
            cli, ["show", "empty_exp", "--storage", f"json://{tmpdir}"]
        )
        assert result.exit_code == 0
        assert "No evaluations found" in result.output

        # Test with all results having errors (covers line 195)
        storage.create_experiment("all_errors_exp")
        eval_err = EvaluationMetadata(
            evaluation_name="error_eval",
            started_at=1234567890.0,
            status=EvaluationStatus.COMPLETED,
        )
        storage.create_evaluation("all_errors_exp", eval_err)
        error_records = [
            Record(
                item_id=i,
                dataset_row={"input": f"test_{i}"},
                scores=[Score("exact_match", False, [accuracy()], {})],
                prompt=None,
                model_response=None,
                error=f"Error {i}",
            )
            for i in range(3)
        ]
        storage.add_results("all_errors_exp", "error_eval", error_records)
        result = runner.invoke(
            cli, ["show", "all_errors_exp", "--storage", f"json://{tmpdir}"]
        )
        assert result.exit_code == 0
        # Should show error summary
        assert "Error Summary" in result.output or "errors" in result.output.lower()

    def test_rename_command(self, tmp_path):
        """Test rename command with real storage operations."""
        tmpdir = tmp_path
        storage = JSONStorage(tmpdir)
        storage.create_experiment("old_name")

        # Add some data to ensure it's preserved
        eval1 = EvaluationMetadata(
            evaluation_name="eval1",
            started_at=1234567890.0,
            status=EvaluationStatus.COMPLETED,
        )
        storage.create_evaluation("old_name", eval1)

        runner = CliRunner()

        # Rename the experiment
        result = runner.invoke(
            cli, ["rename", "old_name", "new_name", "--storage", f"json://{tmpdir}"]
        )
        assert result.exit_code == 0

        # Verify rename worked
        experiments = storage.list_experiments()
        assert "new_name" in experiments
        assert "old_name" not in experiments

        # Verify data was preserved
        evaluations = storage.list_evaluations("new_name")
        assert "eval1" in evaluations

    def test_delete_command(self, tmp_path):
        """Test delete command with real storage operations."""
        tmpdir = tmp_path
        storage = JSONStorage(tmpdir)
        storage.create_experiment("to_delete")
        storage.create_experiment("to_keep")

        runner = CliRunner()

        # Delete one experiment
        result = runner.invoke(
            cli, ["delete", "to_delete", "--storage", f"json://{tmpdir}"]
        )
        assert result.exit_code == 0

        # Verify deletion
        experiments = storage.list_experiments()
        assert "to_delete" not in experiments
        assert "to_keep" in experiments

        # Try to delete non-existent
        result = runner.invoke(
            cli, ["delete", "nonexistent", "--storage", f"json://{tmpdir}"]
        )
        assert result.exit_code == 0
        assert "not found" in result.output

    def test_datasets_command(self):
        """Test datasets command with real dataset implementations."""

        # Create real dataset classes
        class TestDataset1(Dataset):
            name = "test_dataset1"
            splits = ["train", "test", "validation"]
            columns = ["question", "answer", "explanation"]
            num_rows = 1000

            def __init__(self, split=None, **kwargs):
                self.split = split

            def __iter__(self):
                # Return a few sample items
                for i in range(3):
                    yield (f"Question {i}", f"Answer {i}", f"Explanation {i}")

        class TestDataset2(Dataset):
            name = "test_dataset2"
            splits = []  # No splits
            columns = ["input", "output"]
            num_rows = None  # Streaming dataset

            def __init__(self, split=None, **kwargs):
                pass

            def __iter__(self):
                for i in range(2):
                    yield (f"Input {i}", f"Output {i}")

        class BrokenDataset(Dataset):
            name = "broken_dataset"
            splits = ["train"]
            columns = ["data"]

            def __init__(self, split=None, **kwargs):
                raise ValueError("This dataset is broken")

            def __iter__(self):
                yield ("never called",)

        # Register the datasets
        dataset_registry.register(TestDataset1)
        dataset_registry.register(TestDataset2)
        dataset_registry.register(BrokenDataset)

        runner = CliRunner()

        # Test basic listing
        result = runner.invoke(cli, ["datasets"])
        assert result.exit_code == 0
        assert "test_dataset1" in result.output
        assert "test_dataset2" in result.output
        assert "train, test, validation" in result.output or "train" in result.output

        # Test verbose mode
        result = runner.invoke(cli, ["datasets", "--verbose"])
        assert result.exit_code == 0
        assert "test_dataset1" in result.output
        assert "test_dataset2" in result.output
        assert (
            "question, answer, explanation" in result.output
            or "question" in result.output
        )
        assert "@foreach.test_dataset1" in result.output
        assert "@foreach.test_dataset2()" in result.output  # No splits version
        # Broken dataset should be listed (error only happens on instantiation)
        assert "broken_dataset" in result.output

        # Test filtering
        result = runner.invoke(cli, ["datasets", "--name", "dataset1"])
        assert result.exit_code == 0
        assert "test_dataset1" in result.output
        assert "test_dataset2" not in result.output

        # Test filter with no matches
        result = runner.invoke(cli, ["datasets", "--name", "nonexistent"])
        assert result.exit_code == 0
        assert "No datasets found matching" in result.output

        # Test when no datasets available
        # Clear registry
        dataset_registry._dataset_classes.clear()
        result = runner.invoke(cli, ["datasets"])
        assert result.exit_code == 0
        assert "No datasets found" in result.output or "pip install" in result.output

    def test_error_handling(self, tmp_path):
        """Test error scenarios with real storage backend."""
        tmpdir = tmp_path
        storage = JSONStorage(tmpdir)

        runner = CliRunner()

        # Show non-existent experiment
        result = runner.invoke(
            cli, ["show", "nonexistent", "--storage", f"json://{tmpdir}"]
        )
        assert result.exit_code == 0
        assert "not found" in result.output.lower()

        # Rename non-existent experiment
        result = runner.invoke(
            cli, ["rename", "nonexistent", "new", "--storage", f"json://{tmpdir}"]
        )
        assert result.exit_code == 0
        assert "not found" in result.output.lower()

        # Create experiment and try to rename to existing name
        storage.create_experiment("exp1")
        storage.create_experiment("exp2")
        result = runner.invoke(
            cli, ["rename", "exp1", "exp2", "--storage", f"json://{tmpdir}"]
        )
        assert result.exit_code == 0
        assert "already exists" in result.output.lower()

        # Test delete with exception handling
        with patch(
            "dotevals.storage.json.JSONStorage.delete_experiment",
            side_effect=Exception("Storage error"),
        ):
            result = runner.invoke(
                cli, ["delete", "exp1", "--storage", f"json://{tmpdir}"]
            )
            assert result.exit_code == 0
            assert "Error deleting experiment" in result.output

        # Test datasets command with exception
        with patch(
            "dotevals.cli.list_available", side_effect=Exception("Dataset error")
        ):
            result = runner.invoke(cli, ["datasets"])
            assert result.exit_code == 0
            assert "Error listing datasets" in result.output

    def test_custom_storage_plugin(self):
        """Test that custom storage plugins work with real registration."""

        # Create a real custom storage implementation
        class CustomStorage(Storage):
            def __init__(self, path):
                self.path = path
                self.experiments = {
                    "custom_exp1": ["eval1", "eval2"],
                    "custom_exp2": ["eval3"],
                }

            def list_experiments(self):
                return list(self.experiments.keys())

            def list_evaluations(self, experiment_name):
                return self.experiments.get(experiment_name, [])

            def get_results(self, experiment_name, evaluation_name):
                # Return some dummy results
                return [
                    Record(
                        item_id=0,
                        dataset_row={"data": "custom"},
                        scores=[Score("custom_metric", True, [accuracy()], {})],
                        prompt=None,
                        model_response=None,
                    )
                ]

            def create_experiment(self, name):
                self.experiments[name] = []

            def delete_experiment(self, name):
                self.experiments.pop(name, None)

            def rename_experiment(self, old_name, new_name):
                if old_name in self.experiments:
                    self.experiments[new_name] = self.experiments.pop(old_name)

            def create_evaluation(self, experiment_name, evaluation):
                if experiment_name not in self.experiments:
                    self.experiments[experiment_name] = []
                self.experiments[experiment_name].append(evaluation.evaluation_name)

            def load_evaluation(self, experiment_name, evaluation_name):
                if evaluation_name in self.experiments.get(experiment_name, []):
                    return EvaluationMetadata(
                        evaluation_name=evaluation_name,
                        started_at=1234567890.0,
                        status=EvaluationStatus.COMPLETED,
                    )
                return None

            def update_evaluation_status(
                self, experiment_name, evaluation_name, status
            ):
                pass  # No-op for this test

            def add_results(self, experiment_name, evaluation_name, records):
                pass  # No-op for this test

            def completed_items(self, experiment_name, evaluation_name):
                return []

            def remove_error_result(self, experiment_name, evaluation_name, item_id):
                pass

            def remove_error_results_batch(
                self, experiment_name, evaluation_name, item_ids
            ):
                pass

        # Register the custom storage
        storage_registry.register("custom", CustomStorage)

        runner = CliRunner()

        # Use the custom storage with CLI
        result = runner.invoke(cli, ["list", "--storage", "custom://test_path"])
        assert result.exit_code == 0
        assert "custom_exp1" in result.output
        assert "custom_exp2" in result.output

        # Show command with custom storage
        result = runner.invoke(
            cli, ["show", "custom_exp1", "--storage", "custom://test_path"]
        )
        assert result.exit_code == 0
        assert "eval1" in result.output or "custom_metric" in result.output

    def test_multiple_dataset_plugins(self):
        """Test aggregating datasets from multiple plugins with real implementations."""

        # Simulate multiple dataset "plugins" by registering datasets with different prefixes
        class Plugin1Dataset1(Dataset):
            name = "plugin1_dataset1"
            splits = ["train", "test"]
            columns = ["col1", "col2"]
            num_rows = 100

            def __init__(self, split=None, **kwargs):
                self.split = split

            def __iter__(self):
                yield ("data1", "data2")

        class Plugin1Dataset2(Dataset):
            name = "plugin1_dataset2"
            splits = ["train"]
            columns = ["col3"]
            num_rows = 50

            def __init__(self, split=None, **kwargs):
                self.split = split

            def __iter__(self):
                yield ("data3",)

        class Plugin2Dataset1(Dataset):
            name = "plugin2_dataset1"
            splits = []
            columns = ["col4", "col5"]
            num_rows = None

            def __init__(self, split=None, **kwargs):
                pass

            def __iter__(self):
                yield ("data4", "data5")

        # Register all datasets
        dataset_registry.register(Plugin1Dataset1)
        dataset_registry.register(Plugin1Dataset2)
        dataset_registry.register(Plugin2Dataset1)

        runner = CliRunner()

        # List all datasets - should aggregate from all "plugins"
        result = runner.invoke(cli, ["datasets"])
        assert result.exit_code == 0
        assert "plugin1_dataset1" in result.output
        assert "plugin1_dataset2" in result.output
        assert "plugin2_dataset1" in result.output

        # Filter across plugins
        result = runner.invoke(cli, ["datasets", "--name", "dataset1"])
        assert result.exit_code == 0
        assert "plugin1_dataset1" in result.output
        assert "plugin2_dataset1" in result.output
        assert "plugin1_dataset2" not in result.output  # Doesn't match filter


class TestCLIFormatting:
    """Test Rich console formatting - these require mocking."""

    def test_colored_output_warnings(self):
        """Test that CLI uses proper coloring for warnings."""
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            captured_prints = []

            def capture_print(content=None, *args, **kwargs):
                if content is not None:
                    captured_prints.append(str(content))

            with patch("dotevals.cli.console.print", side_effect=capture_print):
                result = runner.invoke(cli, ["list", "--storage", f"json://{tmpdir}"])
                assert result.exit_code == 0

                # Check for yellow warning color
                assert any("[yellow]" in str(p) for p in captured_prints)
                assert any("No experiments found" in str(p) for p in captured_prints)

    def test_colored_output_errors(self):
        """Test that CLI uses red color for errors."""
        runner = CliRunner()

        captured_prints = []

        def capture_print(content=None, *args, **kwargs):
            if content is not None:
                captured_prints.append(str(content))

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("dotevals.cli.console.print", side_effect=capture_print):
                result = runner.invoke(
                    cli, ["show", "nonexistent", "--storage", f"json://{tmpdir}"]
                )
                assert result.exit_code == 0

                # Check for red error color
                assert any("[red]" in str(p) for p in captured_prints)
                assert any("not found" in str(p).lower() for p in captured_prints)

    def test_colored_output_success(self):
        """Test that CLI uses green color for success."""
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            storage = JSONStorage(tmpdir)
            storage.create_experiment("old_name")

            captured_prints = []

            def capture_print(content=None, *args, **kwargs):
                if content is not None:
                    captured_prints.append(str(content))

            with patch("dotevals.cli.console.print", side_effect=capture_print):
                result = runner.invoke(
                    cli,
                    ["rename", "old_name", "new_name", "--storage", f"json://{tmpdir}"],
                )
                assert result.exit_code == 0

                # Check for green success color
                assert any("[green]" in str(p) for p in captured_prints)
                assert any("renamed" in str(p).lower() for p in captured_prints)

    def test_rich_table_creation(self):
        """Test that CLI creates proper Rich tables."""
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            storage = JSONStorage(tmpdir)
            storage.create_experiment("project1")
            storage.create_experiment("20240101_120000_abcd1234")  # ephemeral

            captured_tables = []

            def capture_print(content=None, *args, **kwargs):
                if content is not None and hasattr(content, "add_column"):
                    captured_tables.append(content)

            with patch("dotevals.cli.console.print", side_effect=capture_print):
                result = runner.invoke(cli, ["list", "--storage", f"json://{tmpdir}"])
                assert result.exit_code == 0

                # Should create tables for named and ephemeral experiments
                assert len(captured_tables) >= 1
                # Check table has proper structure
                table = captured_tables[0]
                assert hasattr(table, "title")
                assert hasattr(table, "columns")
