import pytest
from typer.testing import CliRunner

from lumaCLI.luma import app


runner = CliRunner()


@pytest.mark.skip
def test_ingest(test_server, setup_db):
    """
    Test the 'ingest' command of the CLI application to ensure it successfully
    ingests data from a specified source into a PostgreSQL database.

    Args:
    - test_server: A fixture providing the test server URL.
    - setup_db: A fixture providing database connection details.

    The test invokes the CLI 'ingest' command with the necessary arguments
    and checks the exit code and output to verify successful execution.
    """
    result = runner.invoke(
        app,
        [
            "postgres",
            "ingest",
            "--luma-url",
            test_server,
            "--database",
            setup_db.info.dbname,
            "--host",
            setup_db.info.host,
            "--port",
            setup_db.info.port,
            "--username",
            setup_db.info.user,
            "--password",
            setup_db.info.password,
            "--no-config",
        ],
    )
    assert result.exit_code == 0
    assert "The request was successful!" in result.output
