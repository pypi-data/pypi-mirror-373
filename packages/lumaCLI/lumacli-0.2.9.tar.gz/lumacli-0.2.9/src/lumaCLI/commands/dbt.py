"""Ingest dbt metadata into Luma."""

from enum import Enum
from pathlib import Path
import time

import typer
from dbt_artifacts_parser.parser import (
    parse_catalog,
    parse_manifest,
    parse_run_results,
)
from dbt_artifacts_parser.parsers.utils import get_dbt_schema_version
from rich import print
from rich.console import Console
from rich.panel import Panel
import typer

from lumaCLI.utils import (
    check_ingestion_results,
    check_ingestion_status, perform_ingestion_request,
)
from lumaCLI.utils.options import (
    DryRun,
    Follow,
    LumaURL,
    MetadataDir,
)

from lumaCLI.utils.luma_utils import json_path_to_dict

app = typer.Typer(no_args_is_help=True, pretty_exceptions_show_locals=False)
console = Console()


class IngestionStatus(Enum):
    successful = 0
    failed = 1
    pending = 2


# A matrix of supported dbt versions and their corresponding artifact schema versions.
# This provides a clear source of truth for supported versions.
SUPPORTED_DBT_VERSIONS = {
    "https://schemas.getdbt.com/dbt/manifest/v7.json",
    "https://schemas.getdbt.com/dbt/manifest/v11.json",
    "https://schemas.getdbt.com/dbt/manifest/v12.json",
    "https://schemas.getdbt.com/dbt/catalog/v1.json",
    "https://schemas.getdbt.com/dbt/run-results/v4.json",
    "https://schemas.getdbt.com/dbt/run-results/v5.json",
    "https://schemas.getdbt.com/dbt/run-results/v6.json",
}

def _is_supported_dbt_version(dbt_version: str) -> bool:
    """
    Check if the provided dbt version is supported.
    """
    return dbt_version in SUPPORTED_DBT_VERSIONS

def _validate_dbt_version(artifact_dict: dict):
    """
    Check if the dbt version in the artifact dictionary is supported.
    Raises an exception if the version is not supported.
    """
    dbt_version = get_dbt_schema_version(artifact_dict)
    if not _is_supported_dbt_version(dbt_version):
        raise Exception(
            f"Unsupported dbt version: {dbt_version}. Supported versions are: {', '.join(SUPPORTED_DBT_VERSIONS.keys())}"
        )

@app.command()
def validate(
    metadata_dir: Path = MetadataDir,
):
    """
    Validates dbt artifacts (manifest.json, catalog.json, etc.) using dbt-artifacts-parser.
    """
    all_valid = True
    found_any = False
    console.print(
        Panel(f"🔍 Validating artifacts in [cyan]{metadata_dir.absolute()}[/cyan]/")
    )

    def _validate_artifact(file_path, parser_func, artifact_name):
        nonlocal all_valid, found_any
        if not file_path.is_file():
            return

        found_any = True
        try:
            artifact_dict = json_path_to_dict(file_path)
            dbt_version = get_dbt_schema_version(artifact_dict)
            if not _is_supported_dbt_version(dbt_version):
                raise Exception(f"Unsupported dbt version: {dbt_version}"
                    f"Unsupported dbt version: {dbt_version}. Supported versions are: {', '.join(SUPPORTED_DBT_VERSIONS.keys())}"
                )
            parser_func(artifact_dict)
            console.print(f"[green]✔ {artifact_name} is valid.[/green]")
        except Exception as e:
            console.print_exception(show_locals=True)
            console.print(
                Panel(f"[red]{e}[/red]", title=f"Error processing: {artifact_name}:", border_style="red")
            )
            # add traceback to the console output
            console.print(
                Panel(
                    f"[red]Error processing {artifact_name} at {file_path.absolute()}[/red]",
                    border_style="red",
                )
            )
            all_valid = False

    artifacts_to_check = [
        (metadata_dir / "manifest.json", parse_manifest, "manifest.json"),
        (metadata_dir / "catalog.json", parse_catalog, "catalog.json"),
    ]

    for path, artifact_parser, name in artifacts_to_check:
        _validate_artifact(path, artifact_parser, name)

    if not found_any:
        console.print(
            Panel("[bold yellow]No dbt artifacts found to validate.[/bold yellow]")
        )
        raise typer.Exit(1)

    if all_valid:
        console.print(
            Panel("[bold green]✅ All found artifacts are valid![/bold green]")
        )
    else:
        console.print(
            Panel("[bold red]❌ Validation failed for one or more artifacts.[/bold red]")
        )
        raise typer.Exit(1)


@app.command()
def ingest(  # noqa: C901
    metadata_dir: Path = MetadataDir,
    luma_url: str = LumaURL,
    dry_run: bool = DryRun,
    follow: bool = Follow,
):
    """
    Validates and ingests a bundle of dbt artifacts from the specified directory.
    manifest.json and catalog.json are required.
    """
    # Define JSON paths.
    manifest_json_path = metadata_dir / "manifest.json"
    catalog_json_path = metadata_dir / "catalog.json"

    # Ensure required files exist.
    if not manifest_json_path.is_file():
        console.print(
            Panel(f"[red]Required file not found: {manifest_json_path.absolute()}[/red]")
        )
    if not catalog_json_path.is_file():
        console.print(Panel(f"[red]Required file not found: {catalog_json_path.absolute()}[/red]"))
        raise typer.Exit(1)

    console.print(
        Panel(
            f"📦 Preparing dbt artifacts from [cyan]{metadata_dir.absolute()}[/cyan] for ingestion..."
        )
    )

    # Validate and load artifacts
    try:
        manifest_dict = json_path_to_dict(manifest_json_path)
        _validate_dbt_version(manifest_dict)
        manifest_artifact = parse_manifest(manifest_dict)
        console.print("[green]✔ manifest.json validated and loaded.[/green]")

        catalog_dict = json_path_to_dict(catalog_json_path)
        _validate_dbt_version(catalog_dict)
        catalog_artifact = parse_catalog(catalog_dict)
        console.print("[green]✔ catalog.json validated and loaded.[/green]")

    except Exception as e:
        console.print(
            Panel(f"[red]✖ Artifact validation failed:[/red]\n{e}", border_style="red")
        )
        raise e

    # Define bundle dict
    artifacts_bundle = {
        "manifest_json": manifest_artifact.model_dump(by_alias=True, mode='json'),
        "catalog_json": catalog_artifact.model_dump(by_alias=True, mode='json'),
    }

    # If in dry run mode, print the bundle and exit.
    if dry_run:
        print("Dry run mode: Payload with the following keys would be sent:")
        print(list(artifacts_bundle.keys()))
        raise typer.Exit(0)

    # Send ingestion request.
    endpoint = f"{luma_url}/api/v1/dbt/"
    response, ingestion_uuid = perform_ingestion_request(
        url=endpoint,
        method="POST",
        payload=artifacts_bundle,
        verify=False,
    )
    if not response.ok:
        raise typer.Exit(1)

    # Wait until ingestion is complete.
    if follow and ingestion_uuid:
        ingestion_status = None

        with console.status("Waiting...", spinner="dots"):
            for _ in range(30):
                ingestion_status = check_ingestion_status(
                    luma_url, ingestion_uuid, verify=False
                )
                if ingestion_status == IngestionStatus.successful.value:
                    response = check_ingestion_results(luma_url, ingestion_uuid)
                    print()
                    print(f"Ingestion results for ID {ingestion_uuid}:")
                    print()
                    print(response)
                    return

                if ingestion_status == IngestionStatus.failed.value:
                    print()
                    print(f"Ingestion failed for ID {ingestion_uuid}")
                    return

                if ingestion_status == IngestionStatus.pending.value:
                    time.sleep(1)

        if ingestion_status != IngestionStatus.successful.value:
            print(
                f"Ingestion did not complete successfully within the wait period. Status: {ingestion_status}"
            )


@app.command()
def send_test_results(
    metadata_dir: Path = MetadataDir,
    luma_url: str = LumaURL,
    dry_run: bool = DryRun,
    follow: bool = Follow,
):
    """
    Validates and sends 'run_results.json' from the specified directory to Luma.
    """

    # Define the path to 'run_results.json'
    run_results_path = metadata_dir / "run_results.json"

    if not run_results_path.is_file():
        print(Panel(f"[red]File not found: {run_results_path.absolute()}[/red]"))
        raise typer.Exit(1)

    console.print(
        Panel(
            f"📦 Preparing run_results.json from [cyan]{metadata_dir.absolute()}[/cyan]..."
        )
    )

    # Validate and load artifact
    try:
        run_results_dict = json_path_to_dict(run_results_path)
        run_results_artifact = parse_run_results(run_results_dict).model_dump(by_alias=True, mode='json')

        console.print("[green]✔ run_results.json validated and loaded.[/green]")
    except Exception as e:
        console.print(
            Panel(f"[bold red]✖ Artifact validation failed:[/bold red]\n{e}", border_style="red")
        )
        raise typer.Exit(1)

    # If in dry run mode, print the test results and exit.
    if dry_run:
        print("Dry run mode: The following payload would be sent:")
        print(run_results_dict)
        raise typer.Exit(0)

    # Send ingestion request.
    endpoint = f"{luma_url}/api/v1/dbt/run_results/"
    response, ingestion_uuid = perform_ingestion_request(
        url=endpoint,
        method="POST",
        payload=run_results_artifact,
        verify=False,
    )
    if not response.ok:
        raise typer.Exit(1)

    if follow and ingestion_uuid:
        ingestion_status = None

        with console.status("Waiting...", spinner="dots"):
            for _ in range(30):
                ingestion_status = check_ingestion_status(luma_url, ingestion_uuid)
                if ingestion_status == IngestionStatus.successful.value:
                    response = check_ingestion_results(luma_url, ingestion_uuid)
                    print()
                    print(f"Ingestion results for ID {ingestion_uuid}:")
                    print()
                    print(response)
                    return

                if ingestion_status == IngestionStatus.failed.value:
                    print()
                    print(f"Ingestion failed for ID {ingestion_uuid}")
                    return

                if ingestion_status == IngestionStatus.pending.value:
                    time.sleep(1)

        if ingestion_status != IngestionStatus.successful.value:
            print(
                f"Ingestion did not complete successfully within the wait period. Status: {ingestion_status}"
            )


# Run the application.
if __name__ == "__main__":
    app()