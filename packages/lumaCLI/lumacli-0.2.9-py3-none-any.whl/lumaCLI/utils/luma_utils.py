"""Utility functions for the CLI."""

import contextlib
from enum import Enum
import json
from pathlib import Path
import subprocess
import traceback
from typing import Optional, Union

import requests
from rich import print
from rich.console import Console
from rich.panel import Panel
import typer
import yaml

from lumaCLI.models import Config


class IngestionStatus(Enum):
    successful = 0
    failed = 1
    pending = 2


class HttpMethod(str, Enum):
    """HTTP methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    PATCH = "PATCH"


# Create console for rich output
console = Console()

CONFIG_YAML_EXAMPLE = """# Example:
#
# groups:
#   - meta_key: "domain"
#     slug: "domains"
#     label_plural: "Domains"
#     label_singular: "Domain"
#     icon: "Cube"
#     in_sidebar: true
#     visible: true
#   - meta_key: "true_source"
#     slug: "sources"
#     label_plural: "Sources"
#     label_singular: "Source"
#     icon: "Cloud"
#     in_sidebar: true
"""
OWNERS_YAML_EXAMPLE = """# Example:
#
# owners:
#   - email: "some@one.com"
#     first_name: "Dave"
#     last_name: "Smith"
#     title: "Director"
#   - email: "other@person.com"
#     first_name: "Michelle"
#     last_name: "Dunne"
#     title: "CTO"
#   - email: "someone@else.com"
#     first_name: "Dana"
#     last_name: "Pawlak"
#     title: "HR Manager"
"""


def json_path_to_dict(json_path: str | Path) -> Optional[dict]:
    """Converts a JSON file to a Python dictionary.

    Args:
        json_path (str): The path to the JSON file.

    Returns:
        optional[dict]: A dictionary representation of the JSON file, or None if an
            error occurs.
    """
    try:
        with Path.open(json_path, "r") as json_file:
            data = json.load(json_file)
    except Exception:
        data = None
    return data


def run_command(command: str, capture_output: bool = False) -> str | None:
    """Execute a shell command and optionally capture its output.

    Args:
        command (str): The shell command to be executed.
        capture_output (bool, optional): Flag to determine if the command's output
            should be captured. Defaults to False.

    Returns:
        optional[str]: The standard output of the command if `capture_output` is True,
            otherwise None.

    Raises:
        typer.Exit: Exits the script if the command execution fails.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,  # noqa: S602
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        console.print(
            Panel.fit(
                f"[bold red]ERROR[/bold red]: An error occurred while running the command: [bold yellow]{e}[/bold yellow]",
                title="Error",
                border_style="red",
            )
        )
        if e.output:
            console.print(f"[bold cyan]Output[/bold cyan]: {e.output}")
        if e.stderr:
            console.print(f"[bold red]Error[/bold red]: {e.stderr}")
        raise typer.Exit(1) from e

    if capture_output:
        return result.stdout.strip()

    return None


def init_config(config_dir: Path | str = "./.luma", force: bool = False) -> None:
    """Initialize configuration files in the specified directory.

    Args:
        config_dir (Path | str, optional): The directory where configuration files
            will be created. Defaults to "./.luma".
        force (bool, optional): If True, existing configuration files will be
            overwritten. Defaults to False.

    Raises:
        FileExistsError: If configuration files already exist and `force` is not set to
            True.
    """
    config_dir = Path(config_dir)

    config_path = config_dir / "config.yaml"
    owners_path = config_dir / "owners.yaml"

    if force:
        config_path.unlink(missing_ok=True)
        owners_path.unlink(missing_ok=True)
        with contextlib.suppress(FileNotFoundError):
            config_dir.rmdir()

    if not config_path.exists() and not owners_path.exists():
        config_dir.mkdir(exist_ok=True)
        config_path.touch(exist_ok=False)
        owners_path.touch(exist_ok=False)
    else:
        raise FileExistsError

    config_path.write_text(CONFIG_YAML_EXAMPLE)
    owners_path.write_text(OWNERS_YAML_EXAMPLE)


def get_config(config_dir: Path | str = "./.luma") -> Config | None:
    """Retrieve configuration data from YAML files in the specified directory.

    Args:
        config_dir (Path | str, optional): The directory containing the
            configuration files. Defaults to "./.luma".

    Returns:
        optional[Config]: The configuration object if the configuration is successfully
            loaded, otherwise None.

    Raises:
        FileNotFoundError: If the configuration files are missing.
        typer.Abort: If there is an error parsing the YAML files.
    """
    config_dir = Path(config_dir)

    config_path = config_dir / "config.yaml"
    owners_path = config_dir / "owners.yaml"

    config_missing = True
    owners_missing = True

    config_dict = {}
    config_data = {}
    owners_data = {}

    if config_path.exists():
        config_missing = False
        with config_path.open("r") as f:
            try:
                config_data: Optional[dict] = yaml.safe_load(f)
            except yaml.YAMLError as e:
                print(f"Error parsing YAML file: {e}")
                raise typer.Abort() from e

    if owners_path.exists():
        owners_missing = False
        with owners_path.open("r") as f:
            try:
                owners_data: Optional[dict] = yaml.safe_load(f)

            except yaml.YAMLError as e:
                print(f"Error parsing YAML file: {e}")
                raise typer.Abort() from e

    if config_missing and owners_missing:
        raise FileNotFoundError

    if config_data is not None:
        config_dict.update(config_data)

    if owners_data is not None:
        config_dict.update(owners_data)

    return Config(**config_dict)


def print_response(response: requests.Response) -> None:
    """Print Luma API response.

    Args:
        response (requests.Response): The response to print.
    """
    try:
        parsed_response = response.json()
    except Exception:
        parsed_response = None

    if response.ok:
        msg = "[green]The request was successful.[/green]"
        if parsed_response:
            msg += f"\n[yellow]Response:\n{parsed_response}[/yellow]"
        else:
            msg += f"\n[green]Raw response:\n{response.text}[/green]"
    else:
        if parsed_response:
            error_msg = f"\n\nError message: {parsed_response['message']}"
        else:
            error_msg = f"Raw response:\n{response.text}"
        msg = f"[red]The request failed with status code {response.status_code}.{error_msg}[/red]"

    print(msg)

    if not response.ok or parsed_response is None:
        raise typer.Exit(1)


def send_config(
    config: Config, luma_url: str, verify: bool = True
) -> requests.Response:
    """Send configuration data to a specified URL.

    Args:
        config (Config): The configuration data to be sent.
        luma_url (str): The URL where the configuration data will be sent.
        verify (bool, optional): Whether to verify the server's TLS certificate.

    Returns:
        requests.Response: The response from the server after sending the configuration
            data.

    Raises:
        typer.Exit: If there is an error in sending the configuration data.
    """
    print(Panel("[yellow]Sending config info to luma[/yellow]"))

    try:
        response = requests.request(
            method="POST",
            url=f"{luma_url}/api/v1/config",
            json=config.model_dump(by_alias=True),
            verify=False,
            timeout=(
                21.05,
                60 * 30,
            ),
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        error_message = "[red]The config request has failed. Please check your connection and try again."
        if isinstance(e, requests.exceptions.Timeout):
            error_message += " If you're using a VPN, ensure it's properly connected or try disabling it temporarily."
        elif isinstance(e, requests.exceptions.ConnectionError):
            error_message += (
                " This could be due to maximum retries being exceeded or failure to establish a new connection. "
                "Please check your network configuration."
            )
        print(Panel(error_message + "[/red]"))

        # Print the traceback
        traceback_info = traceback.format_exc()
        print(traceback_info)

        raise typer.Exit(1) from e

    if not response.ok:
        print(Panel("[red]Sending config info to luma FAILED[/red]"))

    print_response(response)
    return response


def perform_ingestion_request(
    url: str,
    payload: dict | list | None,
    verify: bool = True,
    method: HttpMethod = HttpMethod.POST,
    timeout: (float | tuple[float, float] | tuple[float, None]) | None = (
        20,
        60 * 30,
    ),
    headers: dict[str, str] | None = None,
    params: dict[str, str | int | float] | None = None,
) -> tuple[requests.Response, str | None]:
    """Send an HTTP request.

    Args:
        url (str): The URL for the request.
        payload (dict | list | None): The payload for the request, if any.
        verify (bool, optional): Whether to verify the server's TLS certificate.
            Defaults to True.
        method (HttpMethod, optional): _description_. Defaults to HttpMethod.POST.
        timeout (optional[float | tuple[float, float] | tuple[float, None]]): The
            timeout for the request. Defaults to (20, 60 * 30).
        headers (optional[dict[str, str]], optional): Headers to be sent with the
            request. Defaults to None.
        params (optional[dict[str, str | int | float]]): URL parameters for the request.
            Defaults to None.

    Raises:
        typer.Exit: In case of timeout or connection error.

    Returns:
        tuple[requests.Response, str | None]: The HTTP response and the ingestion ID.
    """
    print("[yellow]Sending ingestion request to Luma...[/yellow]")

    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=payload,
            verify=verify,
            timeout=timeout,
        )
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        error_message = (
            "The request has failed. Please check your connection and try again."
        )
        if isinstance(e, requests.exceptions.Timeout):
            error_message += " If you're using a VPN, ensure it's properly connected or try disabling it temporarily."
        else:
            error_message += " This could be due to maximum retries being exceeded or failure to establish a new connection. Please check your network configuration."
        print(Panel(f"[red]{error_message}[/red]"))

        # Print the traceback
        traceback_info = traceback.format_exc()
        print(traceback_info)

        raise typer.Exit(1) from e

    print_response(response)

    ingestion_id = response.json().get("ingestion_uuid")
    return response, ingestion_id


def check_ingestion_status(
    luma_url: str, ingestion_uuid: str, verify: bool = True
) -> str:
    """Fetches the status for a specific ingestion ID from Luma.

    Args:
        luma_url (str): The base URL for Luma.
        ingestion_uuid (str): The ingestion ID to fetch the status for.
        verify (bool, optional): Whether to verify the server's TLS certificate.
            Defaults to True.

    Returns:
        str: The status of the ingestion process.
    """
    status_endpoint = f"{luma_url}/api/v1/ingestions/"
    response = requests.get(
        status_endpoint,
        params={"uuid": ingestion_uuid},
        verify=verify,
        timeout=(20, 60 * 30),
    )
    if not response.ok:
        print(
            f"Failed to fetch results for ingestion ID {ingestion_uuid}. HTTP Status: {response.status_code}"
        )
        raise typer.Exit(1)

    response_json = response.json()
    instance = response_json.get("data")
    return instance.get("status")


def check_ingestion_results(
    luma_url: str, ingestion_uuid: str, verify: bool = True
) -> Union[str, dict]:
    """Fetches and interprets the results for a specific ingestion ID.

    Args:
        luma_url (str): The base URL for Luma.
        ingestion_uuid (str): The ingestion ID to check the results for.
        verify (bool, optional): Whether to verify the server's TLS certificate.
            Defaults to True.

    Returns:
        Union[str, dict]: A message describing the status of the ingestion process or
            the JSON response for successful completions.
    """
    status_endpoint = f"{luma_url}/api/v1/ingestions/"
    response = requests.get(
        status_endpoint,
        params={"uuid": ingestion_uuid},
        verify=verify,
        timeout=(20, 60 * 30),
    )
    if not response.ok:
        return f"Failed to fetch results for ingestion ID {ingestion_uuid}. HTTP Status: {response.status_code}"

    response_json = response.json()
    instance = response_json.get("data")
    status = instance.get("status")

    if status == IngestionStatus.pending.value:
        return f"Ingestion ID {ingestion_uuid} is still pending."

    if status == IngestionStatus.failed.value:
        error_details = instance.get("error", "No additional error details provided.")
        return (
            f"Ingestion ID {ingestion_uuid} has failed. Error details: {error_details}"
        )

    if status == IngestionStatus.successful.value:
        # Return the entire JSON response for successful completions
        return instance.get("summary")

    return f"Unrecognized status for ingestion ID {ingestion_uuid}: {status}"
