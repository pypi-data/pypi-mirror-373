"""Manage Luma instance configuration."""

from pathlib import Path

from rich import print
import typer

from lumaCLI.utils import get_config, init_config, send_config
from lumaCLI.utils.options import ConfigDir, DryRun, Force, LumaURL


app = typer.Typer(
    name="config", no_args_is_help=True, pretty_exceptions_show_locals=False
)


@app.command(help="Initialize the configuration.")
def init(config_dir: Path = ConfigDir, force: bool = Force) -> None:
    """Initialize the configuration.

    Args:
        config_dir (Path): The directory to write the configuration files.
        force (bool): If True, overwrite the configuration if it already exists.

    Raises FileExistsError if the configuration already exists and 'force' is not True.
    """
    try:
        init_config(config_dir=config_dir, force=force)
        print(f"[green]Config initialized at[/green] {config_dir}")
    except FileExistsError as e:
        print(
            f"[red]Error![/red] [red]Config files already exist at[/red] {config_dir}\n"
            f"[yellow]If you want to override run with flag [/yellow][red]--force/-f[/red]"
        )
        raise typer.Exit(1) from e


@app.command(help="Display the current configuration information.")
def show(config_dir: Path = ConfigDir) -> None:
    """Display current configuration from the specified directory."""
    try:
        config = get_config(config_dir=config_dir)
        print(config)
    except FileNotFoundError as e:
        print(
            f"[red]Error![/red] [red]Config files not found at[/red] {config_dir}\n"
            "[yellow]To generate config files use [/yellow][white]'luma config init'[/white]"
        )
        raise typer.Exit(1) from e


@app.command(help="Send the current configuration information to luma")
def send(
    config_dir: Path = ConfigDir, luma_url: str = LumaURL, dry_run: bool = DryRun
) -> None:
    """Send configuration to the specified Luma URL.

    In dry run mode, the configuration is printed but not sent.
    """
    try:
        config = get_config(config_dir=config_dir)

        if dry_run:
            print(config.model_dump(by_alias=True))
            return

        if config:
            response = send_config(config=config, luma_url=luma_url)
            if not response.ok:
                raise typer.Exit(1)
        else:
            print(
                f"[red]No Config detected under {config_dir}[/red]\n"
                f"[yellow]To generate config files use [/yellow][white]'luma config init'[/white]"
            )

    except FileNotFoundError as e:
        print(
            f"[red]Error![/red] [red]Config files not found at[/red] {config_dir}\n"
            f"[yellow]To generate config files use [/yellow][white]'luma config init'[/white]"
        )
        raise typer.Exit(1) from e
