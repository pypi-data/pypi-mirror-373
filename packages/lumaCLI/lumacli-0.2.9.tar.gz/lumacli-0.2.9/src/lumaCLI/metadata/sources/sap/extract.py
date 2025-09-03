import dlt


try:
    import pyrfc
    from pyrfc._exception import ABAPApplicationError, ABAPRuntimeError
except ModuleNotFoundError as e:
    msg = "The 'pyrfc' package is required to use the SAPRFC source. "
    raise ImportError(msg) from e
from itertools import batched
import string
import textwrap

from loguru import logger


@dlt.source(name="sap")
def sap(
    ashost: str = dlt.secrets.value,
    sysnr: str = dlt.secrets.value,
    username: str = dlt.secrets.value,
    passwd: str = dlt.secrets.value,
):
    """Query SAP with SQL using the RFC protocol.

    Use the RFC_READ_TABLE to read SAP table metadata.
    """
    delimiter = "\t"

    # Test the connection.
    con = pyrfc.Connection(
        ashost=ashost,
        sysnr=sysnr,
        user=username,
        passwd=passwd,
    )
    logger.info("Checking the connection...")
    try:
        con.ping()
        logger.info("Connection successful.")
    except Exception as e:
        logger.exception("Connection to SAP failed.")
        raise
    finally:
        con.close()

    # By convention, custom tables use a "Z" or "Y" prefix in their name.
    custom_table_prefixes = ["Z", "Y"]
    standard_table_prefixes = [
        char for char in string.ascii_uppercase if char not in custom_table_prefixes
    ]

    def get_response(params):
        """Call the RFC_READ_TABLE function with the given parameters."""
        con = pyrfc.Connection(
            ashost=ashost,
            sysnr=sysnr,
            user=username,
            passwd=passwd,
        )
        try:
            response = con.call("RFC_READ_TABLE", **params)
        except (ABAPApplicationError, ABAPRuntimeError) as e:
            if e.key == "DATA_BUFFER_EXCEEDED":
                msg = "Character limit per row exceeded. Please select fewer columns."
            elif e.key == "TSV_TNEW_PAGE_ALLOC_FAILED":
                msg = "Memory allocation failed; try a smaller batch size."
            else:
                msg = f"Error while calling RFC_READ_TABLE with params:\n{params}."
            logger.exception(msg)
            raise
        finally:
            con.close()

        # Process the response into records.
        record_key = "WA"
        data_raw = response["DATA"]
        data = [
            [value.strip() for value in row[record_key].split(delimiter)]
            for row in data_raw
        ]
        logger.info(f"Retrieved {len(data)} rows.")
        columns = params["FIELDS"]
        return [dict(zip(columns, row)) for row in data]

    def get_table_schema(table_prefixes: list[str]):
        conditions = [f"TABNAME LIKE '{prefix}%'" for prefix in table_prefixes]
        # Each line in OPTIONS must be ≤72 characters.
        grouped = textwrap.wrap(" OR ".join(conditions), width=72)
        options = [{"TEXT": line} for line in grouped]
        # Filter out internal SAP objects.
        options += [{"TEXT": " AND TABCLASS = 'TRANSP'"}]
        params = {
            "QUERY_TABLE": "DD02L",
            "FIELDS": ["TABNAME"],
            "OPTIONS": options,
            "DELIMITER": delimiter,
        }
        yield get_response(params)

    @dlt.resource(
        name="standard_tables", write_disposition="merge", primary_key="TABNAME"
    )
    def standard_tables():
        """Get a list of standard SAP tables."""
        yield get_table_schema(standard_table_prefixes)

    @dlt.resource(write_disposition="merge", primary_key="TABNAME")
    def custom_tables():
        """Get a list of custom SAP tables."""
        yield get_table_schema(custom_table_prefixes)

    def get_table_details(table_names):
        """Get metadata about SAP tables."""
        table_batches = batched(table_names, 1000)
        for batch_number, batch in enumerate(table_batches, start=1):
            conditions = [f"TABNAME = '{table}'" for table in batch]
            # Each line in OPTIONS must be ≤72 characters.
            grouped = textwrap.wrap(" OR ".join(conditions), width=72)
            options = [{"TEXT": line} for line in grouped]
            params = {
                "QUERY_TABLE": "DD03L",
                "FIELDS": ["TABNAME", "FIELDNAME", "DATATYPE", "LENG"],
                "OPTIONS": options,
                "DELIMITER": delimiter,
            }
            logger.info(f"Extracting table batch number {batch_number}...")
            yield get_response(params)

    @dlt.transformer(
        data_from=standard_tables,
        write_disposition="merge",
        primary_key=("TABNAME", "FIELDNAME"),
    )
    def standard_tables_details(standard_tables):
        standard_table_names = [row["TABNAME"] for row in standard_tables]
        yield get_table_details(standard_table_names)

    @dlt.transformer(
        data_from=custom_tables,
        write_disposition="merge",
        primary_key=("TABNAME", "FIELDNAME"),
    )
    def custom_tables_details(custom_tables):
        custom_table_names = [row["TABNAME"] for row in custom_tables]
        yield get_table_details(custom_table_names)

    @dlt.resource(write_disposition="merge", primary_key="ROLLNAME")
    def column_details():
        """Get metadata about table columns in SAP tables."""
        params = {
            "QUERY_TABLE": "DD04T",
            "FIELDS": ["ROLLNAME", "DDTEXT"],
            "OPTIONS": [{"TEXT": "DDLANGUAGE = 'EN'"}],
            "DELIMITER": delimiter,
        }
        logger.info("Extracting table columns...")
        yield get_response(params)

    return [
        standard_tables,
        standard_tables_details,
        custom_tables,
        custom_tables_details,
        column_details,
    ]


if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="sap", destination="duckdb", dataset_name="bronze"
    )
    # pipeline.run(sap.with_resources("column_details", "custom_tables_details"))
    pipeline.run(sap().with_resources("column_details", "standard_tables_details"))
