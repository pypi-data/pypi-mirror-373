"""Extract a database table manifest from SAP metadata.

We use the local DuckDB instance to join the two source tables in order to be able
to produce models expected by Luma.

Manifests are saved in batches (50,000 tables per batch) in order to limit payload size.
"""

from itertools import batched

import dlt
from loguru import logger

from lumaCLI.metadata.models.database import (
    DatabaseTable,
    DatabaseTableColumn,
    DatabaseTableManifest,
    DatabaseTableSchemaMetadata,
)


pipeline = dlt.pipeline(
    pipeline_name="sap", destination="duckdb", dataset_name="bronze"
)

custom_tables_query = """
SELECT tabname, fieldname, datatype, leng, ddtext
FROM custom_tables_details
LEFT JOIN column_details ON custom_tables_details.fieldname = column_details.rollname
ORDER BY tabname
"""

standard_tables_query = """
SELECT tabname, fieldname, datatype, leng, ddtext
FROM standard_tables_details
LEFT JOIN column_details ON standard_tables_details.fieldname = column_details.rollname
ORDER BY tabname
"""


def transform():
    with (
        pipeline.sql_client() as client,
        client.execute_query(standard_tables_query) as cursor,
    ):
        table_to_columns = {}
        # Create a table -> columns mapping.
        for i, df in enumerate(cursor.iter_df(chunk_size=50000)):
            logger.info(
                f"Extracting table->column mappings from chunk {i} ({len(df)} rows)..."
            )
            for _, row in df.iterrows():
                table_name = row["tabname"]
                column = DatabaseTableColumn(
                    name=row["fieldname"],
                    type=row["datatype"],
                    length=str(row["leng"]),
                    description=row["ddtext"],
                )
                if table_name not in table_to_columns:
                    table_to_columns[table_name] = {"columns": []}
                table_to_columns[table_name]["columns"].append(column)

    # Create table manifests from the mapping.
    tables = (
        DatabaseTable(
            name=table_name, columns=table_to_columns[table_name]["columns"], type="sap"
        )
        for table_name in table_to_columns
    )
    batch_size = 50000
    for i, table_batch in enumerate(batched(tables, batch_size)):
        logger.info(f"Generating manifest for table batch {i}...")

        manifest = DatabaseTableManifest(
            metadata=DatabaseTableSchemaMetadata(schema="database_table", version=1),
            payload=list(table_batch),
        )

        yield manifest

        # logger.info(f"Writing {len(manifest.payload)} tables to batch {i} manifest...")

        # with open(f"database_table_manifest__batch_{i}.json", "w") as f:
        #     f.write(manifest.json())
