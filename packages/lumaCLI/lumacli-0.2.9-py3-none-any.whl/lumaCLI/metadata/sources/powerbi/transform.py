import json
from pathlib import Path
import re

from lumaCLI.metadata.models.bi import (
    Dashboard,
    DashboardManifest,
    DashboardSchemaMetadata,
    DataModel,
)
from lumaCLI.metadata.sources.powerbi.models import WorkspaceInfo


def transform(workspace_info: WorkspaceInfo) -> DashboardManifest:
    # Extract tables from the Power BI metadata.
    tables = extract_tables(workspace_info)
    reports = extract_reports(workspace_info, tables=tables)

    return DashboardManifest(
        metadata=DashboardSchemaMetadata(schema="dashboard", version=1),
        payload=reports,
    )


def extract_tables(workspace_info) -> list[dict]:
    tables = []
    # Each dataset table can only have one database table as a source.
    for workspace in workspace_info.workspaces:
        for dataset in workspace.datasets:
            for dataset_table in dataset.tables:
                if dataset_table.source is None:
                    continue

                # Extract the underlying database table.
                source_expression = dataset_table.source[0].expression
                table_database_table = _extract_table_from_expression(source_expression)

                if not table_database_table:
                    continue

                database_table_name = table_database_table["name"]
                tables.append({
                    "dataset_id": dataset.id,
                    "dataset_table_name": dataset_table.name,
                    "database_table_name": database_table_name,
                    "database_table_schema": table_database_table.get("schema"),
                    "database_table_database": table_database_table.get("database"),
                    "columns": [column.name for column in dataset_table.columns],
                })
    return tables


def extract_reports(
    workspace_info: WorkspaceInfo, tables: list[dict]
) -> list[Dashboard]:
    reports = []
    for workspace in workspace_info.workspaces:
        for report in workspace.reports:
            # We're not interested in PowerBI Apps. Not sure why they're included
            #  - either way, the original report the app is based on is already included
            # in the response.
            if report.name.startswith("[App]"):
                continue

            report_filtered = {}
            report_id = report.id
            report_filtered["external_id"] = report_id
            report_filtered["url"] = (
                "https://app.powerbi.com/groups/" + workspace.id
                or "" + "/reports/" + report_id
            )
            report_filtered["type"] = "powerbi"
            report_filtered["name"] = report.name
            report_filtered["workspace"] = workspace.name
            report_filtered["created_at"] = report.createdDateTime
            report_filtered["modified_at"] = report.modifiedDateTime
            report_filtered["owners"] = [
                {
                    "user_id": user.graphId,
                    "username": user.identifier,
                    "name": user.displayName,
                }
                for user in report.users
                if user.reportUserAccessRight == "Owner"
            ]

            report_tables = [
                {
                    "name": table["database_table_name"],
                    "schema": table["database_table_schema"],
                    "database": table["database_table_database"],
                    "columns": table["columns"],
                }
                for table in tables
                if table["dataset_id"] == report.datasetId
            ]
            report_filtered["parent_models"] = report_tables

            reports.append(report_filtered)

    return reports


def _extract_table_from_expression(expression: str) -> DataModel | None:
    """Extract schema and table name from expression."""
    # Check if this is a NativeQuery - we don't extract from those
    if "Value.NativeQuery" in expression:
        return None

    # Get database name.
    database_name_expr = re.search(
        r'AmazonRedshift\.Database\s*\(\s*".*?"\s*,\s*"([^" ]+)"\s*\)',
        expression,
        re.IGNORECASE,
    )
    if not database_name_expr:
        return None
    database_name = database_name_expr.group(1).strip()

    # Find source variable assigned to AmazonRedshift.Database
    source_pattern = r"(\w+)\s*=\s*AmazonRedshift\.Database\s*\([^)]+\)"
    source_match = re.search(source_pattern, expression, re.IGNORECASE)

    if not source_match:
        return None

    source_var_name = source_match.group(1).strip()

    # Get schema names.
    schema_pattern = (
        rf'(\w+)\s*=\s*{re.escape(source_var_name)}\s*{{\[Name="([^"]+)"\]}}\[Data\]'
    )
    schema_match = re.findall(schema_pattern, expression, re.IGNORECASE)

    if not schema_match:
        return None

    schema_var_name = schema_match[0][0].strip()  # The variable name given by user.
    schema_name = schema_match[0][1].strip()  # The actual database schema name.

    # Get table metadata.
    table_pattern = (
        r"\w+\s*=\s*" + re.escape(schema_var_name) + r'{\[Name="([^" ]+)"\]}\[Data\]'
    )
    table_match = re.findall(table_pattern, expression, re.IGNORECASE)

    if not table_match:
        return None

    return {
        "name": table_match[0].strip(),
        "schema": schema_name.strip(),
        "database": database_name,
    }


def _extract_dataflow_table_from_expression(expression: str) -> DataModel | None:
    """Extract schema and table name from dataflow expression."""
    # Look for pattern: Source{[entity="table_name"]}[Data]
    entity_pattern = r'{\[entity="([^"]+)"\]}\[Data\]'
    entity_match = re.search(entity_pattern, expression, re.IGNORECASE)

    if not entity_match:
        return None

    table_name = entity_match.group(1).strip()

    return {
        "name": table_name,
        "schema": None,
        "database": None,
    }


if __name__ == "__main__":
    with Path("powerbi_workspace_info.json").open(encoding="utf-8") as f:
        workspace_info = json.load(f)

    dashboard_manifest = transform(workspace_info)

    with Path("powerbi_extracted.json").open("w", encoding="utf-8") as f:
        f.write(dashboard_manifest.json(by_alias=True))
    # # print(json.dumps(tables, indent=4))
