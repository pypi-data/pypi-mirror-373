import json
import re
import shutil
import time
from datetime import datetime
from pathlib import Path

import click
from rich import box
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

from dotevals.datasets import get_dataset_info, list_available
from dotevals.storage import registry
from dotevals.summary import EvaluationSummary

console = Console()


@click.group()
def cli() -> None:
    """dotevals CLI to manage experiments and evaluations."""


@cli.command()
@click.option("--name", help="Filter experiments by name.")
@click.option("--storage", default="json://.dotevals", help="Storage backend path")
def list(name: str | None, storage: str) -> None:
    """List available experiments"""
    storage_backend = registry.get_storage(storage)
    experiment_names = storage_backend.list_experiments()

    # Separate ephemeral and named experiments
    ephemeral_experiments = []
    named_experiments = []
    ephemeral_pattern = re.compile(r"^\d{8}_\d{6}_[a-f0-9]{8}$")

    for exp_name in experiment_names:
        if exp_name == ".dotevals":
            continue
        elif ephemeral_pattern.match(exp_name):
            ephemeral_experiments.append(exp_name)
        else:
            named_experiments.append(exp_name)

    if not named_experiments and not ephemeral_experiments:
        console.print(f"[yellow]No experiments found at {storage}.[/yellow]")
        return

    # Show named experiments first
    if named_experiments:
        table = Table(title="Named Experiments", box=box.SIMPLE)
        table.add_column("Experiment Name")
        table.add_column("Evaluations")

        for experiment_name in sorted(named_experiments):
            if name and name not in experiment_name:
                continue

            evaluations = storage_backend.list_evaluations(experiment_name)
            table.add_row(experiment_name, str(len(evaluations)))

        console.print(table)

    # Show ephemeral experiments
    if ephemeral_experiments:
        ephemeral_table = Table(title="Ephemeral Experiments", box=box.SIMPLE)
        ephemeral_table.add_column("Timestamp")
        ephemeral_table.add_column("Evaluations")

        for experiment_name in sorted(ephemeral_experiments, reverse=True):
            if name and name not in experiment_name:
                continue

            evaluations = storage_backend.list_evaluations(experiment_name)
            # Extract timestamp from path
            timestamp = (
                experiment_name.split("/")[-1]
                if "/" in experiment_name
                else experiment_name
            )
            ephemeral_table.add_row(timestamp, str(len(evaluations)))

        if named_experiments:
            console.print()  # Add spacing
        console.print(ephemeral_table)


@cli.command()
@click.argument("experiment_name")
@click.option("--storage", default="json://.dotevals", help="Storage backend path")
@click.option("--evaluation", help="Show specific evaluation results.")
@click.option("--full", is_flag=True, help="Show full details.")
@click.option("--errors", is_flag=True, help="Show detailed error information.")
def show(
    experiment_name: str, storage: str, evaluation: str | None, full: bool, errors: bool
) -> None:
    """Show results of an experiment."""
    storage_backend = registry.get_storage(storage)

    # Check if experiment exists
    experiments = storage_backend.list_experiments()
    if experiment_name not in experiments:
        console.print(f"[red]Experiment '{experiment_name}' not found.[/red]")
        return

    # Get all evaluations for this experiment
    evaluation_names = storage_backend.list_evaluations(experiment_name)

    if not evaluation_names:
        console.print(
            f"[yellow]No evaluations found for experiment '{experiment_name}'.[/yellow]"
        )
        return

    # Filter to specific evaluation if requested
    if evaluation:
        if evaluation not in evaluation_names:
            console.print(
                f"[red]Evaluation '{evaluation}' not found in experiment '{experiment_name}'.[/red]"
            )
            return
        evaluation_names = [evaluation]

    # Process each evaluation
    for eval_name in evaluation_names:
        # Get results for this evaluation
        results = storage_backend.get_results(experiment_name, eval_name)

        if full:
            # Show raw JSON data
            content = json.dumps(
                [
                    {
                        "item_id": r.item_id,
                        "dataset_row": r.dataset_row,
                        "prompt": r.prompt,
                        "model_response": r.model_response,
                        "scores": [
                            {
                                "name": s.name,
                                "value": s.value,
                                "metrics": [m.__name__ for m in s.metrics],
                                "metadata": s.metadata,
                            }
                            for s in r.scores
                        ],
                        "error": r.error,
                        "timestamp": r.timestamp,
                    }
                    for r in results
                ],
                indent=2,
            )
            syntax = Syntax(content, "json", theme="monokai", line_numbers=True)
            console.print(f"\n[bold]Evaluation: {eval_name}[/bold]")
            console.print(syntax)
            continue

        # Display summary table
        table = Table(
            title=f"Summary of {experiment_name} :: {eval_name}", box=box.SIMPLE
        )
        table.add_column("Evaluator")
        table.add_column("Metric")
        table.add_column("Score", justify="right")
        table.add_column("Errors", justify="right")

        # Count errors
        total_items = len(results)
        error_count = sum(1 for result in results if result.error is not None)
        error_percentage = (error_count / total_items * 100) if total_items > 0 else 0

        # Create evaluation summary
        summary = EvaluationSummary(results).summary if results else {}

        for evaluator, metrics in summary.items():
            for metric_name, score in metrics.items():
                error_display = f"{error_count}/{total_items} ({error_percentage:.1f}%)"
                if error_count > 0:
                    error_display = f"[red]{error_display}[/red]"
                    # Calculate metric excluding errors
                    successful_results = [r for r in results if r.error is None]
                    if successful_results:
                        # Recompute metric for successful results only
                        successful_summary = EvaluationSummary(
                            successful_results
                        ).summary
                        score_without_errors = successful_summary.get(
                            evaluator, {}
                        ).get(metric_name, 0)
                        score_display = (
                            f"{score:.2f} ({score_without_errors:.2f} excluding errors)"
                        )
                    else:
                        score_display = f"{score:.2f}"
                else:
                    score_display = f"{score:.2f}"
                table.add_row(evaluator, metric_name, score_display, error_display)

        console.print(table)

        # Show error summary if there are errors
        if error_count > 0:
            console.print("\n[bold]Error Summary:[/bold]")
            console.print(
                f"Total errors: [red]{error_count}[/red] out of {total_items} items ({error_percentage:.1f}%)"
            )

            # Group errors by type
            error_types: dict[str, list[int]] = {}  # type: ignore[valid-type]
            for result in results:
                if result.error:
                    # Extract error type from the error message
                    error_type = (
                        result.error.split(":")[0] if ":" in result.error else "Unknown"
                    )
                    error_types[error_type] = error_types.get(error_type, 0) + 1

            if error_types:
                console.print("\nError Types:")
                for error_type, count in sorted(
                    error_types.items(), key=lambda x: x[1], reverse=True
                ):
                    console.print(
                        f" • {error_type}: {count} occurrence{'s' if count > 1 else ''}"
                    )

        # Show detailed errors if --errors flag is used
        if errors and error_count > 0:
            console.print(f"\n[bold]Error Details ({error_count} errors):[/bold]\n")
            error_idx = 0
            for result in results:
                if result.error:
                    error_idx += 1
                    console.print(
                        f"[bold][{error_idx}] Item ID: {result.item_id}[/bold]"
                    )
                    console.print(f"    Error: [red]{result.error}[/red]")

                    # Display dataset row (truncated if too long)
                    dataset_str = str(result.dataset_row)
                    if len(dataset_str) > 100:
                        dataset_str = dataset_str[:97] + "..."
                    console.print(f"    Dataset: {dataset_str}")

                    # Display timestamp
                    timestamp = datetime.fromtimestamp(result.timestamp).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    console.print(f"    Time: {timestamp}\n")


@cli.command()
@click.argument("old_name")
@click.argument("new_name")
@click.option("--storage", default="json://.dotevals", help="Storage backend path")
def rename(old_name: str, new_name: str, storage: str) -> None:
    """Rename an experiment."""
    storage_backend = registry.get_storage(storage)

    # Check if experiment exists
    experiments = storage_backend.list_experiments()
    if old_name not in experiments:
        console.print(f"[red]Experiment '{old_name}' not found.[/red]")
        return

    # Check if new name already exists
    if new_name in experiments:
        console.print(f"[red]Experiment '{new_name}' already exists.[/red]")
        return

    storage_backend.rename_experiment(old_name, new_name)
    console.print(f"[green]Experiment '{old_name}' renamed to '{new_name}'[/green]")


@cli.command()
@click.argument("experiment_name")
@click.option("--storage", default="json://.dotevals", help="Storage backend path")
def delete(experiment_name: str, storage: str) -> None:
    """Delete an experiment."""
    storage_backend = registry.get_storage(storage)

    # Check if experiment exists
    experiments = storage_backend.list_experiments()
    if experiment_name not in experiments:
        console.print(
            f"[red]Experiment '{experiment_name}' not found. Run 'dotevals list' to list the available experiments.[/red]"
        )
        return

    try:
        storage_backend.delete_experiment(experiment_name)
        console.print(f"[green]Deleted experiment '{experiment_name}'[/green]")
    except Exception as e:
        console.print(f"[red]Error deleting experiment: {e}[/red]")


@cli.command()
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be deleted without actually deleting",
)
@click.option(
    "--older-than",
    default=7,
    type=int,
    help="Only delete directories older than this many days (default: 7)",
)
@click.option("--yes", is_flag=True, help="Skip confirmation prompt")
def cleanup(dry_run, older_than, yes):
    """Remove old ephemeral evaluation artifacts from .dotevals directory."""
    dotevals_dir = Path(".dotevals")

    if not dotevals_dir.exists():
        console.print("[yellow]No .dotevals directory found.[/yellow]")
        return

    # Pattern for ephemeral directories: YYYYMMDD_HHMMSS_hexhash
    ephemeral_pattern = re.compile(r"^\d{8}_\d{6}_[a-f0-9]{8}$")
    cutoff_time = time.time() - (older_than * 86400)

    # Find directories to clean
    to_delete = []
    total_size = 0

    for entry in dotevals_dir.iterdir():
        if entry.is_dir() and ephemeral_pattern.match(entry.name):
            try:
                mtime = entry.stat().st_mtime
                if mtime < cutoff_time:
                    # Calculate size
                    size = sum(
                        f.stat().st_size for f in entry.rglob("*") if f.is_file()
                    )
                    to_delete.append((entry, mtime, size))
                    total_size += size
            except (OSError, PermissionError) as e:
                console.print(f"[yellow]Warning: Cannot access {entry}: {e}[/yellow]")

    if not to_delete:
        console.print(
            f"[green]No ephemeral directories older than {older_than} days found.[/green]"
        )
        return

    # Display what will be deleted
    console.print(
        f"\n[bold]Found {len(to_delete)} ephemeral directories to clean:[/bold]"
    )

    table = Table(box=box.ROUNDED)
    table.add_column("Directory", style="cyan")
    table.add_column("Age (days)", justify="right")
    table.add_column("Size", justify="right")

    for dir_path, mtime, size in sorted(to_delete, key=lambda x: x[1]):
        age_days = int((time.time() - mtime) / 86400)
        size_mb = size / (1024 * 1024)
        table.add_row(dir_path.name, str(age_days), f"{size_mb:.2f} MB")

    console.print(table)
    console.print(
        f"\n[bold]Total size to free: {total_size / (1024 * 1024):.2f} MB[/bold]"
    )

    if dry_run:
        console.print("\n[yellow]DRY RUN - No files were deleted.[/yellow]")
        return

    # Confirm deletion
    if not yes:
        if not click.confirm("\nDo you want to delete these directories?"):
            console.print("[yellow]Cleanup cancelled.[/yellow]")
            return

    # Perform deletion
    deleted_count = 0
    errors = []

    for dir_path, _, _ in to_delete:
        try:
            shutil.rmtree(dir_path)
            deleted_count += 1
        except Exception as e:
            errors.append((dir_path.name, str(e)))

    # Report results
    if deleted_count > 0:
        console.print(
            f"\n[green]✓ Successfully deleted {deleted_count} directories.[/green]"
        )
        console.print(
            f"[green]Freed {total_size / (1024 * 1024):.2f} MB of disk space.[/green]"
        )

    if errors:
        console.print("\n[red]Failed to delete some directories:[/red]")
        for name, error in errors:
            console.print(f"  - {name}: {error}")


@cli.command()
@click.option(
    "--verbose", "-v", is_flag=True, help="Show detailed information for each dataset"
)
@click.option(
    "--name", "-n", help="Filter datasets by name (case-insensitive partial match)"
)
def datasets(verbose: bool, name: str | None) -> None:
    """List available datasets and their details."""
    try:
        available_datasets = list_available()

        if not available_datasets:
            console.print("[yellow]No datasets found.[/yellow]")
            console.print("\nTo use datasets, install a dataset plugin:")
            console.print("  pip install dotevals-datasets")
            return

        # Filter by name if provided
        if name:
            available_datasets = [
                d for d in available_datasets if name.lower() in d.lower()
            ]
            if not available_datasets:
                console.print(f"[yellow]No datasets found matching '{name}'.[/yellow]")
                return

        if verbose:
            # Show detailed information for each dataset
            for dataset_name in sorted(available_datasets):
                try:
                    info = get_dataset_info(dataset_name)

                    # Create a table for this dataset
                    table = Table(title=f"Dataset: {dataset_name}", box=box.ROUNDED)
                    table.add_column("Property", style="cyan", no_wrap=True)
                    table.add_column("Value", style="white")

                    # Add dataset properties
                    table.add_row("Name", info["name"])
                    splits_display = (
                        ", ".join(info["splits"]) if info["splits"] else "No splits"
                    )
                    table.add_row("Splits", splits_display)
                    table.add_row("Columns", ", ".join(info["columns"]))

                    num_rows = info.get("num_rows")
                    if num_rows is not None:
                        table.add_row("Rows", f"{num_rows:,}")
                    else:
                        table.add_row("Rows", "Unknown (streaming dataset)")

                    console.print(table)
                    console.print()  # Add spacing between datasets

                    # Show usage example
                    console.print("[bold]Usage:[/bold]")
                    if info["splits"]:
                        # Dataset has splits - show example with first split
                        example_split = info["splits"][0]
                        console.print(f'  @foreach.{dataset_name}("{example_split}")')
                    else:
                        # Dataset has no splits - show usage without split parameter
                        console.print(f"  @foreach.{dataset_name}()")
                    columns_str = ", ".join(info["columns"])
                    console.print(f"  def eval_{dataset_name}({columns_str}, model):")
                    console.print("      # Your evaluation logic here")
                    console.print("      pass")
                    console.print()

                except Exception as e:
                    console.print(
                        f"[red]Error loading dataset '{dataset_name}': {e}[/red]"
                    )
                    console.print()
        else:
            # Show summary table
            table = Table(title="Available Datasets", box=box.SIMPLE)
            table.add_column("Dataset", style="cyan", no_wrap=True)
            table.add_column("Splits", style="green")
            table.add_column("Columns", style="yellow")
            table.add_column("Rows", justify="right", style="blue")

            for dataset_name in sorted(available_datasets):
                try:
                    info = get_dataset_info(dataset_name)
                    splits = (
                        ", ".join(info["splits"]) if info["splits"] else "No splits"
                    )
                    columns = ", ".join(info["columns"])
                    num_rows = info.get("num_rows")
                    rows_str = f"{num_rows:,}" if num_rows else "streaming"

                    table.add_row(dataset_name, splits, columns, rows_str)
                except Exception as e:
                    table.add_row(
                        dataset_name, f"[red]Error: {str(e)[:30]}...[/red]", "", ""
                    )

            console.print(table)
            console.print()
            console.print(
                "[dim]Use --verbose for detailed information and usage examples[/dim]"
            )

    except Exception as e:
        console.print(f"[red]Error listing datasets: {e}[/red]")
        console.print("\nMake sure you have dataset plugins installed:")
        console.print("  pip install dotevals-datasets")


if __name__ == "__main__":
    cli()
