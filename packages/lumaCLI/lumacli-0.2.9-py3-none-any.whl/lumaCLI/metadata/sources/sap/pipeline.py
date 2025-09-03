from typing import Generator

from loguru import logger

from lumaCLI.metadata.models.database import DatabaseTableManifest
from lumaCLI.metadata.sources.sap.extract import sap
from lumaCLI.metadata.sources.sap.transform import transform


def pipeline() -> Generator[DatabaseTableManifest, None, None]:
    """Pipeline to extract SAP metadata and."""
    source = sap().with_resources("column_details", "custom_tables_details")
    manifest_batches = transform()
    yield from manifest_batches


if __name__ == "__main__":
    manifest_batches = pipeline()
    for i, manifest in enumerate(manifest_batches):
        logger.info(f"Writing {len(manifest.payload)} tables to batch {i} manifest...")

        with open(f"database_table_manifest__batch_{i}.json", "w") as f:
            f.write(manifest.json())
