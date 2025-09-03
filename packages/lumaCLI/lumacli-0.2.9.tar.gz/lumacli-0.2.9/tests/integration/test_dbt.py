import pytest

from lumaCLI.luma import app
from typer.testing import CliRunner

runner = CliRunner()

METADATA_FIXTURE_NAMES = ["METADATA_DIR_V1_7", "METADATA_DIR_V1_9"]

@pytest.mark.parametrize("metadata_dir_fixture", METADATA_FIXTURE_NAMES)
def test_ingest(request, metadata_dir_fixture):

    metadata_dir = request.getfixturevalue(metadata_dir_fixture)

    result = runner.invoke(
        app,
        [
            "dbt",
            "ingest",
            "--metadata-dir",
            metadata_dir / "model_metadata",
            "--luma-url",
            "http://localhost:8000",
            "--dry-run",
        ],
    )
    assert result.exit_code == 0


@pytest.mark.parametrize("metadata_dir_fixture", METADATA_FIXTURE_NAMES)
def test_ingest_with_shorthand(request, metadata_dir_fixture):

    metadata_dir = request.getfixturevalue(metadata_dir_fixture)

    result = runner.invoke(
        app,
        [
            "dbt",
            "ingest",
            "-m",
            metadata_dir / "model_metadata",
            "-l",
            "http://localhost:8000",
            "-D",
        ],
    )
    assert result.exit_code == 0
    assert "Dry run mode" in result.stdout
