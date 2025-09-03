"""Ingest PostgreSQL metadata into Luma."""

from pathlib import Path
from typing import Any

from requests import Response
from rich import print
from rich.panel import Panel
import typer

from lumaCLI.models import Config
from lumaCLI.utils import (
    get_config,
    get_db_metadata,
    perform_ingestion_request,
    send_config,
)
from lumaCLI.utils.options import (
    ConfigDir,
    DryRun,
    LumaURL,
    NoConfig,
)


app = typer.Typer(no_args_is_help=True, pretty_exceptions_show_locals=False)


@app.command()
def ingest(
    luma_url: str = LumaURL,
    username: str = typer.Option(
        ...,
        "--username",
        "-u",
        envvar="LUMA_POSTGRES_USERNAME",
        help="The username for the PostgreSQL database.",
        prompt="PostgreSQL username",
    ),
    database: str = typer.Option(
        ...,
        "--database",
        "-d",
        envvar="LUMA_POSTGRES_DATABASE",
        help="The name of the PostgreSQL database.",
        prompt="PostgreSQL database",
    ),
    host: str = typer.Option(
        "localhost",
        "--host",
        "-h",
        envvar="LUMA_POSTGRES_HOST",
        help="The host address of the PostgreSQL database.",
    ),
    port: str = typer.Option(
        "5432",
        "--port",
        "-p",
        envvar="LUMA_POSTGRES_PORT",
        help="The port number for the PostgreSQL database.",
    ),
    password: str = typer.Option(
        ...,
        "--password",
        "-P",
        envvar="LUMA_POSTGRES_PASSWORD",
        help="The password for the PostgreSQL database.",
        prompt="PostgreSQL password",
        hide_input=True,
    ),
    dry_run: bool = DryRun,
    config_dir: Path = ConfigDir,
    no_config: bool = NoConfig,
) -> Response:
    """Ingest metadata from PostgreSQL database into a Luma ingestion endpoint."""
    should_send_config = not no_config
    config = None

    if should_send_config:
        try:
            config: Config = get_config(config_dir=config_dir)
        except FileNotFoundError:
            print(
                Panel(
                    "[blue]No config files found. Continuing with the operation...[/blue]"
                )
            )

    # Retrieve database metadata.
    db_metadata: dict[str, list[dict[str, Any]]] = get_db_metadata(
        username=username, database=database, host=host, port=port, password=password
    )

    # In dry run mode, print the database metadata and exit.
    if dry_run:
        print(db_metadata)
        raise typer.Exit(0)

    endpoint = f"{luma_url}/api/v1/postgres"

    # Send ingestion request.
    if config and should_send_config:
        send_config(config=config, luma_url=luma_url)

    response = perform_ingestion_request(
        url=endpoint,
        method="POST",
        payload=db_metadata,
        verify=False,
    )
    if not response.ok:
        raise typer.Exit(1)

    return response


if __name__ == "__main__":
    app()
