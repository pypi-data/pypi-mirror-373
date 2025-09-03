"""A command-line interface (CLI) for the Luma application.

Provides commands for database operations, configuration management, and more.
"""

from enum import Enum
from importlib import import_module
import importlib.metadata
import json
import sys
import time
from typing import Union

from loguru import logger
import requests
from rich import print
from rich.console import Console
import typer
import urllib3

from lumaCLI.commands import config, dbt, postgres
from lumaCLI.utils import (
    check_ingestion_results,
    check_ingestion_status,
    perform_ingestion_request,
)
from lumaCLI.utils.options import (
    DryRun,
    Follow,
    FollowTimeout,
    IngestionId,
    LumaURL,
)
from lumaCLI.utils.state import state


# Set the logging level to INFO by default.
logger.remove()
logger.add(sys.stdout, level="INFO")


__version__ = importlib.metadata.version(__package__ or __name__)

# Disable warnings related to insecure requests for specific cases
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

console = Console()


class MetadataSource(str, Enum):
    """Available metadata sources."""

    POWERBI = "powerbi"
    QLIK_SENSE = "qlik_sense"
    SAP = "sap"


class IngestionStatus(Enum):
    successful = 0
    failed = 1
    pending = 2


# Create a Typer application with configured properties
app = typer.Typer(
    name="luma",
    no_args_is_help=True,
    pretty_exceptions_enable=True,
    pretty_exceptions_show_locals=False,
    pretty_exceptions_short=True,
)


def version_callback(show_version: bool) -> str | None:
    """Print the version of the application.

    Args:
        show_version (bool): If True, shows the version.
    """
    if show_version:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(  # noqa: ARG001
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show the version and exit.",
    ),
    config_dir: str = typer.Option(
        None,
        "--config-dir",
        "-c",
        envvar="LUMA_CONFIG_DIR",
        help="The directory containing the Luma configuration file.",
    ),
) -> None:
    """Main function for the Typer application.

    Args:
        version (bool): Flag to show the version and exit.
        config_dir (str): The directory containing the Luma configuration file.
    """
    state["config_dir"] = config_dir


@app.command()
def status(
    ingestion_id: IngestionId,
    luma_url: str = LumaURL,
) -> Union[str, dict]:
    """Retrieve the status of an ingestion."""
    results = check_ingestion_results(luma_url, ingestion_id)
    print(f"Ingestion results for ID {ingestion_id}:")
    print(results)
    return results


@app.command()
def ingest(
    source: MetadataSource,
    luma_url: str = LumaURL,
    dry_run: bool = DryRun,
    follow: bool = Follow,
    follow_timeout: int = FollowTimeout,
) -> tuple[list[requests.Response], list[str | None]]:
    """Ingest metadata from external sources into Luma."""
    endpoint = f"{luma_url}/api/v1/ingest/dashboard"
    module = import_module(f"lumaCLI.metadata.sources.{source.value}.pipeline")

    # Retrieve generated manifest(s) and send them to Luma.
    manifests = module.pipeline()
    responses = []
    ingestion_ids = []
    for manifest in manifests:
        payload = json.loads(manifest.json(by_alias=True))
        n_items = len(payload["payload"])

        logger.debug(
            f"Sending {n_items} items from {source.value} metadata source to Luma instance {luma_url}..."
        )

        # If in dry run mode, print the bundle and exit.
        if dry_run:
            print(payload)
            raise typer.Exit(0)

        # Send ingestion request.
        response, ingestion_id = perform_ingestion_request(
            url=endpoint, payload=payload
        )
        if not response.ok:
            raise typer.Exit(1)

        if follow and ingestion_id:
            ingestion_status = None

            with console.status("Waiting...", spinner="dots"):
                for _ in range(follow_timeout):
                    ingestion_status = check_ingestion_status(luma_url, ingestion_id)
                    if ingestion_status == IngestionStatus.successful.value:
                        response = check_ingestion_results(luma_url, ingestion_id)
                        print()
                        print(f"Ingestion results for ID {ingestion_id}:")
                        print()
                        print(response)

                    if ingestion_status == IngestionStatus.failed.value:
                        print()
                        print(f"Ingestion failed for ID {ingestion_id}")

                    if ingestion_status == IngestionStatus.pending.value:
                        time.sleep(1)

            if ingestion_status != IngestionStatus.successful.value:
                status_human_readable = IngestionStatus(ingestion_status).name
                print(
                    f"Ingestion did not complete successfully within {follow_timeout} seconds. Status: {status_human_readable}."
                )

        responses.append(response)
        ingestion_ids.append(ingestion_id)

    return responses, ingestion_ids


# Add commands to the Typer application
app.add_typer(dbt.app, name="dbt", help="Ingest metadata from dbt.")
app.add_typer(postgres.app, name="postgres", help="Ingest metadata from Postgres.")
app.add_typer(config.app, name="config", help="Manage Luma instance configuration.")
