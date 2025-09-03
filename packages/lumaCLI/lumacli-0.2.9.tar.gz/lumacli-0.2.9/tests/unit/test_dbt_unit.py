from unittest.mock import patch
import os
from pathlib import Path

import pytest
from typer.testing import CliRunner

from lumaCLI.commands.dbt import validate, IngestionStatus
from lumaCLI.luma import app

runner = CliRunner()

METADATA_PATH_FIXTURES = ["METADATA_DIR_V1_7", "METADATA_DIR_V1_9"]

SUCCESS = 0
FAILURE = 1

@pytest.mark.parametrize("metadata_dir_fixture", METADATA_PATH_FIXTURES)
def test_ingest_requires_only_manifest_and_catalog_json(
    test_server, request, metadata_dir_fixture
):
    """
    Test if 'ingest' requires only manifest.json and catalog.json.
    Parameterized to run against multiple dbt versions.
    """
    # Use the 'request' fixture to get the actual value of the fixture
    # whose name is passed as a string (e.g., "METADATA_DIR_V1_7")
    metadata_dir = f"{request.getfixturevalue(metadata_dir_fixture)}/model_metadata"

    # Get result when the required files are present
    result_no_changes = _get_result(test_server, "ingest", metadata_dir=metadata_dir)

    # Get result when the rest of the json files are missing
    result_manifest_missing = _get_result_whilst_file_missing(
        test_server, "ingest", "manifest.json", metadata_dir=metadata_dir
    )
    result_catalog_missing = _get_result_whilst_file_missing(
        test_server, "ingest", "catalog.json", metadata_dir=metadata_dir
    )

    # Check ingest works when no files are changed, or sources.json or run_results.json are missing
    assert result_no_changes.exit_code == SUCCESS
    assert result_manifest_missing.exit_code == FAILURE
    assert result_catalog_missing.exit_code == FAILURE


@pytest.mark.parametrize("metadata_dir_fixture", METADATA_PATH_FIXTURES)
def test_send_test_results_with_shorthand(
    test_server, request, metadata_dir_fixture
):
    """
    Test if 'send-test-results' with shorthand '-m' requires only run_results.json.
    Parameterized to run against multiple dbt versions.
    """
    # Use the 'request' fixture to get the actual value of the fixture
    metadata_dir = f"{request.getfixturevalue(metadata_dir_fixture)}/model_run_metadata"

    # Get result when the required files are present
    result = _get_result_with_shorthand(
        test_server, "send-test-results", metadata_dir=metadata_dir
    )

    assert result.exit_code == SUCCESS


@pytest.mark.parametrize("metadata_dir_fixture", METADATA_PATH_FIXTURES)
def test_send_test_results_with_shorthand(
    test_server, request, metadata_dir_fixture
):
    """
    Test if 'send-test-results' with shorthand '-m' requires only run_results.json.
    Parameterized to run against multiple dbt versions.
    """
    # Use the 'request' fixture to get the actual value of the fixture
    metadata_dir = f"{request.getfixturevalue(metadata_dir_fixture)}/model_run_metadata"

    # Get result when the required files are present
    result = _get_result_with_shorthand(
        test_server, "send-test-results", metadata_dir=metadata_dir
    )

    assert result.exit_code == SUCCESS


@pytest.mark.parametrize("metadata_dir_fixture", METADATA_PATH_FIXTURES)
def test_send_test_results(
    test_server, request, metadata_dir_fixture
):
    """
    Test if 'send-test-results' requires only run_results.json.
    Parameterized to run against multiple dbt versions.
    """
    # Use the 'request' fixture to get the actual value of the fixture
    metadata_dir = f"{request.getfixturevalue(metadata_dir_fixture)}/model_run_metadata"

    # Get result when the required files are present
    result = _get_result(
        test_server, "send-test-results", metadata_dir=metadata_dir
    )

    assert result.exit_code == SUCCESS


@pytest.mark.parametrize("metadata_dir_fixture", METADATA_PATH_FIXTURES)
def test_send_test_results_dry_run_with_shorthand(
    test_server, request, metadata_dir_fixture
):
    """
    Test if 'send-test-results' with shorthand '-D' correctly performs a dry run.
    Parameterized to run against multiple dbt versions.
    """
    # Use the 'request' fixture to get the actual value of the fixture
    metadata_dir = f"{request.getfixturevalue(metadata_dir_fixture)}/model_run_metadata"

    # Get result when the required files are present
    result = runner.invoke(
        app,
        [
            "dbt",
            "send-test-results",
            "-m",
            metadata_dir,
            "-l",
            test_server,
            "-D",
        ],
    )

    assert result.exit_code == SUCCESS
    assert "Dry run mode" in result.stdout





@pytest.mark.parametrize("metadata_dir_fixture", METADATA_PATH_FIXTURES)
def test_dbt_validate_on_valid_files(test_server, request, metadata_dir_fixture):
    """
    Test if 'dbt validate' works with the provided metadata directory.
    Parameterized to run against multiple dbt versions.
    """
    metadata_dir = f"{request.getfixturevalue(metadata_dir_fixture)}/model_metadata"

    try:
        validate(metadata_dir=Path(metadata_dir))
    except Exception as exc:
        assert False, f"validate raised an exception {exc}"

def test_dbt_validate_on_missing_files():
    """
    Test if 'dbt validate' fails on non-existing paths.
    Parameterized to run against multiple dbt versions.
    """
    metadata_dir = f"dummy"

    with pytest.raises(Exception):
        validate(metadata_dir=Path(metadata_dir))


def _get_result_whilst_file_missing(test_server, command, file_name, metadata_dir):
    """Rename a file, run the command, and rename it back."""
    original_path = os.path.join(metadata_dir, file_name)
    renamed_path = os.path.join(metadata_dir, f"missing_{file_name}")

    os.rename(original_path, renamed_path)
    try:
        result = _get_result(test_server, command, metadata_dir=metadata_dir)
    finally:
        os.rename(renamed_path, original_path)
    return result


def _get_result(test_server, command, metadata_dir):
    """Invoke the CLI runner and return the result."""
    result = runner.invoke(
        app,
        [
            "dbt",
            command,
            "--metadata-dir",
            metadata_dir,
            "--luma-url",
            test_server,
        ],
    )
    return result


def _get_result_with_shorthand(test_server, command, metadata_dir):
    """Invoke the CLI runner with shorthand and return the result."""
    result = runner.invoke(
        app,
        [
            "dbt",
            command,
            "-m",
            metadata_dir,
            "-l",
            test_server,
        ],
    )
    return result


