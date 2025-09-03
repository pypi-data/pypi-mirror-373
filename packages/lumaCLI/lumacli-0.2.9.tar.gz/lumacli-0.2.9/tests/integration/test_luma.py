import uuid

from lumaCLI.luma import app
from typer.testing import CliRunner

runner = CliRunner()


def test_status():
    fake_uuid = uuid.uuid4()
    result = runner.invoke(
        app,
        ["status", "--luma-url", "http://localhost:8000", "--ingestion-id", fake_uuid],
    )
    assert result.exit_code == 0
