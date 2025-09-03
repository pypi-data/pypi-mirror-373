import socket
from pathlib import Path
from time import sleep

import multiprocess
import psycopg2
import pytest
import uvicorn
from fastapi import FastAPI, HTTPException
from pytest_postgresql import factories

app = FastAPI()


@app.post("/api/v1/dbt")
async def dbt(body: dict):
    if body is None:
        raise HTTPException(400)
    return body


@app.post("/api/v1/dbt/run_results")
async def run_results(body: dict):
    if body is None:
        raise HTTPException(400)
    return body


@app.post("/api/v1/postgres")
async def postgres(body: dict):
    if body is None:
        raise HTTPException(400)
    return body


@app.post("/api/v1/config")
async def config(body: dict):
    if body is None:
        raise HTTPException(400)
    return body


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def test_server():
    port = find_free_port()
    server = multiprocess.Process(
        target=uvicorn.run,
        args=(app,),
        kwargs={"host": "0.0.0.0", "port": port},
        daemon=True,
    )
    server.start()
    sleep(1)  # Time to wait while the server starts up
    yield f"http://0.0.0.0:{port}"
    server.terminate()


@pytest.fixture(scope="module")
def config_dir(LUMA_CONFIG_DIR):
    config_dir = Path(LUMA_CONFIG_DIR)
    config_path = config_dir / "config.yaml"
    owners_path = config_dir / "owners.yaml"

    config_dir.mkdir(exist_ok=True)
    config_path.touch()
    with config_path.open("w") as f:
        f.write(
            """groups:
  - meta_key: "domain"
    slug: "domains"
    label_plural: "Domains"
    label_singular: "Domain"
    icon: "Cube"
    in_sidebar: true
    visible: true
  - meta_key: "true_source"
    slug: "sources"
    label_plural: "Sources"
    label_singular: "Source"
    icon: "Cloud"
    in_sidebar: false
"""
        )
    owners_path.touch()
    with owners_path.open("w") as f:
        f.write(
            """owners:
- email: "some@one.com"
  first_name: "Dave"
  last_name: "Smith"
  title: "Director"
- email: "other@person.com"
  first_name: "Michelle"
  last_name: "Dunne"
  title: "CTO"
- email: "someone@else.com"
  first_name: "Dana"
  last_name: "Pawlak"
  title: "HR Manager"
"""
        )
    yield config_dir

    config_path.unlink()
    owners_path.unlink()
    config_dir.rmdir()


@pytest.fixture(scope="module")
def config_dir_invalid_schema(INVALID_SCHEMA_LUMA_CONFIG_DIR):
    config_dir = Path(INVALID_SCHEMA_LUMA_CONFIG_DIR)
    config_path = config_dir / "config.yaml"
    owners_path = config_dir / "owners.yaml"

    config_dir.mkdir(exist_ok=True)
    config_path.touch()
    with config_path.open("w") as f:
        f.write(
            """groups:
  - meta_key: ["domain"]
    slug: ["domains"]
    label_plural: "Domains"
    label_singular: "Domain"
    icon: "Cube"
  - meta_key: ["true_source"]
    slug: "sources"
    label_plural: "Sources"
    label_singular: "Source"
    icon: "Cloud"
"""
        )
    owners_path.touch()
    with config_path.open("w") as f:
        f.write(
            """owners:
- email: "some@one.com"
  first_name: "Dave"
  last_name: "Smith"
  title: "Director"
- email: "Director.com"
  first_name: "Michelle"
  last_name: "Dunne"
  title: "CTO"
- email:["someone@else.com"]
  first_name: "Dana"
  last_name: "Pawlak"
  title: "HR Manager"
"""
        )
    yield config_dir
    config_path.unlink()
    owners_path.unlink()
    config_dir.rmdir()


# This fixture creates a Postgres database
postgresql_proc = factories.postgresql_proc(port=find_free_port())
postgresql = factories.postgresql("postgresql_proc")


@pytest.fixture(scope="function")
def setup_db(postgresql):
    # Get the connection details from the postgresql fixture
    user = postgresql.info.user
    password = postgresql.info.password
    dbname = postgresql.info.dbname
    host = postgresql.info.host
    port = postgresql.info.port

    conn = psycopg2.connect(
        dbname=dbname, user=user, password=password, host=host, port=port
    )
    cur = conn.cursor()

    # Creating tables and inserting test data
    cur.execute(
        """
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50),
            email VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        INSERT INTO users (name, email) VALUES
            ('John Doe', 'john@example.com'),
            ('Jane Smith', 'jane@example.com'),
            ('Mike Johnson', 'mike@example.com');
        
        CREATE TABLE products (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            price DECIMAL(10, 2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        INSERT INTO products (name, price) VALUES
            ('Product A', 19.99),
            ('Product B', 9.99),
            ('Product C', 14.99);
        
        CREATE TABLE orders (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users (id),
            product_id INTEGER REFERENCES products (id),
            quantity INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        INSERT INTO orders (user_id, product_id, quantity) VALUES
            (1, 1, 2),
            (2, 2, 1),
            (3, 3, 3);

        CREATE OR REPLACE VIEW user_orders AS
        SELECT
            users.name AS user_name,
            users.email AS user_email,
            products.name AS product_name,
            orders.quantity AS order_quantity,
            orders.created_at AS order_date
        FROM
            users
        JOIN
            orders ON users.id = orders.user_id
        JOIN
            products ON products.id = orders.product_id;

        CREATE OR REPLACE VIEW product_sales AS
        SELECT
            products.name AS product_name,
            SUM(orders.quantity) AS total_quantity_sold,
            SUM(orders.quantity * products.price) AS total_revenue
        FROM
            products
        JOIN
            orders ON products.id = orders.product_id
        GROUP BY
            products.name;
    """
    )

    connection.commit()
    cursor.close()

    yield connection

    cursor = connection.cursor()
    cursor.execute("DROP SCHEMA test_schema;")
    connection.commit()
    connection.close()


@pytest.fixture(scope="module")
def TESTS_DIR():
    return Path(__file__).parent

@pytest.fixture(scope="module")
def METADATA_DIR_V1_7(TESTS_DIR):
    return TESTS_DIR / "assets" / "dbt_v1.7"


@pytest.fixture(scope="module")
def METADATA_DIR_V1_9(TESTS_DIR):
    return TESTS_DIR / "assets" / "dbt_v1.9"


@pytest.fixture(scope="module")
def INVALID_SCHEMA_LUMA_CONFIG_DIR(TESTS_DIR):
    return TESTS_DIR / ".invalid_schema_luma"


@pytest.fixture(scope="module")
def LUMA_CONFIG_DIR(TESTS_DIR):
    return TESTS_DIR / ".luma"
