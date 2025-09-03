import pytest

from lumaCLI.utils import (
    create_conn,
    generate_pg_dump_content,
    get_db_metadata,
    get_pg_dump_tables_info,
    get_pg_dump_views_info,
    get_tables_row_counts,
    get_tables_size_info,
    run_command,
)
from unittest import skip


@pytest.mark.skip()
def test_run_command():
    """
    Test the `run_command` function to ensure it correctly executes shell commands
    and returns the output.
    """
    command = 'echo "Hello, World!"'
    assert run_command(command, True) == "Hello, World!"


@pytest.mark.skip()
def test_create_conn(setup_db):
    """
    Test the `create_conn` function to ensure it creates a database connection 
    using provided credentials and connection information.
    """
    assert isinstance(
        setup_db.info.port, int
    )  # Add this line to ensure port is an integer

    conn = create_conn(
        username=setup_db.info.user,
        password=setup_db.info.password,
        host=setup_db.info.host,
        port=setup_db.info.port,
        database=setup_db.info.dbname,
    )
    assert conn
    assert conn.closed == 0  # 0 indicates connection is open


@pytest.mark.skip()
def test_generate_pg_dump_content(setup_db):
    """
    Test the `generate_pg_dump_content` function to ensure it correctly generates 
    PostgreSQL database dump content.
    """
    result = generate_pg_dump_content(
        username=setup_db.info.user,
        password=setup_db.info.password,
        host=setup_db.info.host,
        port=setup_db.info.port,
        database=setup_db.info.dbname,
    )
    assert "users" in result
    assert "products" in result
    assert "product_id" in result
    assert "user_id" in result
    assert "CURRENT_TIMESTAMP" in result


@pytest.mark.skip()
def test_get_pg_dump_tables_info(setup_db):
    """
    Test the `get_pg_dump_tables_info` function to validate extraction of table 
    information from PostgreSQL dump content.
    """
    dump_content = generate_pg_dump_content(
        username=setup_db.info.user,
        password=setup_db.info.password,
        host=setup_db.info.host,
        port=setup_db.info.port,
        database=setup_db.info.dbname,
    )
    result = get_pg_dump_tables_info(dump_content)
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.skip()
def test_get_pg_dump_views_info(setup_db):
    """
    Test the `get_pg_dump_views_info` function to validate extraction of view 
    information from PostgreSQL dump content.
    """
    dump_content = generate_pg_dump_content(
        username=setup_db.info.user,
        password=setup_db.info.password,
        host=setup_db.info.host,
        port=setup_db.info.port,
        database=setup_db.info.dbname,
    )
    result = get_pg_dump_views_info(dump_content)
    assert isinstance(result, list)
    assert len(result) > 0


@pytest.mark.skip()
def test_get_tables_size_info(setup_db):
    """
    Test the `get_tables_size_info` function to ensure it retrieves information 
    about the size of tables in a database.
    """
    result = get_tables_size_info(
        username=setup_db.info.user,
        password=setup_db.info.password,
        host=setup_db.info.host,
        port=setup_db.info.port,
        database=setup_db.info.dbname,
    )
    assert isinstance(result, dict)
    assert len(result) > 0


@pytest.mark.skip()
def test_get_tables_row_counts(setup_db):
    """
    Test the `get_tables_row_counts` function to ensure it retrieves row counts 
    for each table in a database.
    """
    result = get_tables_row_counts(
        username=setup_db.info.user,
        password=setup_db.info.password,
        host=setup_db.info.host,
        port=setup_db.info.port,
        database=setup_db.info.dbname,
    )
    assert isinstance(result, dict)
    assert len(result) > 0


@pytest.mark.skip()
def test_get_db_metadata(setup_db):
    """
    Test the `get_db_metadata` function to ensure it retrieves metadata for a 
    database.
    """
    result = get_db_metadata(
        username=setup_db.info.user,
        password=setup_db.info.password,
        host=setup_db.info.host,
        port=setup_db.info.port,
        database=setup_db.info.dbname,
    )
    assert isinstance(result, dict)
    assert len(result) > 0
