"""Common Typer options."""
import os
from pathlib import Path
from typing import Annotated

import typer
from lumaCLI.utils.luma_utils import console
from rich import print
from rich.panel import Panel
import typer


def get_metadata_directory(metadata_dir: str | None, ctx: typer.Context) -> Path | None | str:
    """Return the current working directory if 'metadata_dir' is not specified.

    If 'metadata_dir' is provided, it returns the specified directory.

    Args:
        metadata_dir (str | None): Path to the metadata directory.
        ctx (typer.Context): Context of the current Typer command execution.

    Returns:
        Path: The current working directory or the specified metadata directory.
    """
    # Fix CLI completion; see
    # https://typer.tiangolo.com/tutorial/options/callback-and-context/#fix-completion-using-the-context.
    if ctx.resilient_parsing:
        return None

    if metadata_dir is not None:
        return metadata_dir
    cwd = Path(os.getcwd())
    console.print(
        Panel(
            f"[bold yellow]'metadata_dir' not specified, using current working directory {cwd}[/bold yellow]"
        )
    )
    return cwd


MetadataDir: Path = typer.Option(
    None,
    "--metadata-dir",
    "-m",
    callback=get_metadata_directory,
    help="Specify the directory with dbt metadata files.",
    exists=True,
    dir_okay=True,
    resolve_path=True,
)

ConfigDir: Path = typer.Option(
    "./.luma",
    "--config-dir",
    "-c",
    help="Specify the directory with the config files. Defaults to ./.luma",
    envvar="LUMA_CONFIG_DIR",
    dir_okay=True,
    resolve_path=True,
)

Force: bool = typer.Option(
    False,
    "--force",
    "-f",
    help="Force the operation.",
)

DryRun: bool = typer.Option(
    False,
    "--dry-run",
    "-D",
    help="Perform a dry run. Print the payload but do not send it.",
)

NoConfig: bool = typer.Option(
    False,
    "--no-config",
    "-n",
    help="Set this flag to prevent sending configuration data along with the request.",
)

Follow: bool = typer.Option(
    False, "--follow", help="Follow the ingestion process until it's completed."
)

IngestionId = Annotated[str, typer.Argument(help="Ingestion ID.")]

LumaURL: str = typer.Option(
    "http://localhost:8000",
    "--luma-url",
    "-l",
    help="URL of the luma instance.",
    envvar="LUMA_URL",
)

FollowTimeout: int = typer.Option(
    30,
    "--follow-timeout",
    "-t",
    help="How many seconds to wait for the ingestion process to complete.",
    envvar="LUMA_TIMEOUT",
)
