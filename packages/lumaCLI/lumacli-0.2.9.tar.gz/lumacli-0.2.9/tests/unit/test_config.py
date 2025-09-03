import click
from rich.console import Console
from typer.testing import CliRunner

from lumaCLI.luma import app
from lumaCLI.utils.luma_utils import get_config


runner = CliRunner()


def test_get_config(config_dir):
    """Test if the configuration is correctly retrieved from a given directory."""
    config = get_config(config_dir=config_dir)
    assert config
    assert config.groups is not None
    assert config.owners is not None


def test_show(config_dir):
    """Test if the 'show' command correctly displays the configuration."""
    result = runner.invoke(
        app,
        [
            "config",
            "show",
            "--config-dir",
            config_dir,
        ],
    )

    assert result.exit_code == 0
    config = get_config(config_dir=config_dir)
    console = Console(record=True)
    console.print(config)
    text = console.export_text()
    assert text in result.output


def test_send(config_dir, test_server):
    """Test if the 'send' command successfully sends the configuration."""
    result = runner.invoke(
        app,
        ["config", "send", "--config-dir", config_dir, "--luma-url", test_server],
    )

    assert result.exit_code == 0
    assert "The request was successful" in result.output


def test_show_with_shorthand(config_dir):
    """Test if the 'show' command with shorthand '-c' correctly displays the configuration."""
    result = runner.invoke(
        app,
        [
            "config",
            "show",
            "-c",
            config_dir,
        ],
    )

    assert result.exit_code == 0
    config = get_config(config_dir=config_dir)
    console = Console(record=True)
    console.print(config)
    text = console.export_text()
    assert text in result.output


def test_send_with_shorthand(config_dir, test_server):
    """Test if the 'send' command with shorthand '-c' successfully sends the configuration."""
    result = runner.invoke(
        app,
        ["config", "send", "-c", config_dir, "-l", test_server],
    )

    assert result.exit_code == 0
    assert "The request was successful" in result.output


def test_init_force_with_shorthand(tmp_path):
    """Test if the 'init' command with shorthand '-f' correctly overwrites an existing configuration."""
    # Create a temporary directory for the config files
    config_dir = tmp_path / ".luma"
    config_dir.mkdir()

    # Create dummy config files
    (config_dir / "config.yaml").touch()
    (config_dir / "owners.yaml").touch()

    # Run the init command with the --force flag
    result = runner.invoke(
        app,
        [
            "config",
            "init",
            "-c",
            str(config_dir),
            "-f",
        ],
    )

    assert result.exit_code == 0
    assert "Config initialized at" in result.output


# Invalid schema tests
def test_get_config_invalid_schema(config_dir_invalid_schema):
    """Test if the configuration retrieval correctly handles an invalid schema."""
    try:
        config = get_config(config_dir=config_dir_invalid_schema)
        assert config is None
    except click.exceptions.Abort:
        pass


def test_show_invalid_schema(config_dir_invalid_schema):
    """Test if the 'show' command correctly handles an invalid configuration schema."""
    result = runner.invoke(
        app,
        [
            "config",
            "show",
            "--config-dir",
            config_dir_invalid_schema,
        ],
    )

    assert result.exit_code == 1
    assert "Error parsing YAML file" in result.output


def test_send_invalid_schema(config_dir_invalid_schema, test_server):
    """Test if the 'send' command correctly handles an invalid configuration schema."""
    result = runner.invoke(
        app,
        [
            "config",
            "send",
            "--config-dir",
            config_dir_invalid_schema,
            "--luma-url",
            test_server,
        ],
    )

    assert result.exit_code == 1
    assert "Error parsing YAML file" in result.output
