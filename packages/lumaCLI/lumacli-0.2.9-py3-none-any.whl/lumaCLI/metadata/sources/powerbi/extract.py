"""Download lineage information from PowerBI API."""

from collections.abc import Generator
from pathlib import Path
from time import sleep
from typing import Any

from azure.identity import ClientSecretCredential
import dlt
from dlt.common import logger
from dlt.sources.helpers.rest_client import RESTClient
from dlt.sources.helpers.rest_client.auth import OAuth2AuthBase
from dlt.sources.helpers.rest_client.paginators import SinglePagePaginator


Workspace = dict[str, Any]


class PowerBIOauthClientCredentials(OAuth2AuthBase):
    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        """PowerBI OAuth2 client credentials authentication.

        Args:
            tenant_id (str): The Azure tenant ID.
            client_id (str): The client ID of the service principal app.
            client_secret (str): The client secret of the service principal app.
        """
        super().__init__()
        self.access_token = self._get_token(tenant_id, client_id, client_secret)

    @staticmethod
    def _get_token(tenant_id: str, client_id: str, client_secret: str) -> str:
        scope = "https://analysis.windows.net/powerbi/api/.default"
        client_secret_credential_class = ClientSecretCredential(
            tenant_id=tenant_id, client_id=client_id, client_secret=client_secret
        )
        return client_secret_credential_class.get_token(scope).token


@dlt.source(name="powerbi")
def powerbi(
    tenant_id: str = dlt.secrets.value,
    client_id: str = dlt.secrets.value,
    client_secret: str = dlt.secrets.value,
) -> dict:
    """The PowerBI metadata source.

    Args:
        tenant_id (str, optional): The Azure tenant ID. Defaults to dlt.secrets.value.
        client_id (str, optional): The client ID of the service principal app. Defaults
            to dlt.secrets.value.
        client_secret (str, optional): The client secret of the service principal app.
            Defaults to dlt.secrets.value.

    Returns:
        dict: _description_

    Yields:
        Iterator[dict]: _description_
    """
    client = RESTClient(
        base_url="https://api.powerbi.com/v1.0/myorg",
        auth=PowerBIOauthClientCredentials(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
        ),
        paginator=SinglePagePaginator(),
    )

    @dlt.resource(primary_key="id", write_disposition="replace")
    def workspaces() -> Generator[list[dict[str, Any]], None, None]:
        endpoint = "groups"
        yield client.get(endpoint).json()["value"]

    # We need to add the type hint for our custom column here as this is required for
    # dbt-osmosis to correctly generate the bronze properties file, and consequently,
    # for dbt-ibis to work.
    @dlt.transformer(
        data_from=workspaces, columns={"description": {"data_type": "text"}}
    )
    def workspaces_lineage(
        workspaces: list[Workspace],
    ) -> Generator[list[Workspace], None, None]:
        workspace_ids = [workspace["id"] for workspace in workspaces]
        request_lineage_endpoint = "admin/workspaces/getInfo"
        params = {
            "lineage": True,
            "datasourceDetails": True,
            "datasetSchema": True,
            "datasetExpressions": True,
            "getArtifactUsers": True,
        }
        body = {"workspaces": workspace_ids}

        # Request a workspace lineage scan and await scan completion.
        response = client.post(request_lineage_endpoint, params=params, json=body)
        scan_id = response.json()["id"]
        scan_status = None
        logger.info("Waiting for scan to complete...")
        while scan_status != "Succeeded":
            scan_status_endpoint = f"admin/workspaces/scanStatus/{scan_id}"
            scan_status = client.get(scan_status_endpoint).json()["status"]
            sleep(0.2)

        # Get the scan result.
        scan_result_endpoint = f"admin/workspaces/scanResult/{scan_id}"
        response = client.get(scan_result_endpoint)
        lineage = response.json()

        # Add "description" column if it doesn't exist.
        # This is required as the schema returned by PowerBI REST API is dynamic, which
        # can break everything downstream. For example, if a workspace description is
        # not set, instead of returning "description": "", PBI REST API simply omits the
        # "description" key.
        for i, workspace in enumerate(lineage["workspaces"]):
            if "description" not in workspace:
                lineage["workspaces"][i]["description"] = ""

        yield lineage

    return [workspaces_lineage]


if __name__ == "__main__":
    import json

    # for workspace in powerbi():
    # print(f"Workspace lineage:\n{workspace}")
    # logger.info(json.dumps(workspace, indent=4))
    with Path("powerbi_workspace_info.json").open("w", encoding="utf-8") as f:
        json.dump(list(powerbi()), f, indent=4)
