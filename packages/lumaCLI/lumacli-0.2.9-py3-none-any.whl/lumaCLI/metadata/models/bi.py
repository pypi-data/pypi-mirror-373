from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class DataModel(BaseModel):
    name: str
    schema_field: str = Field(..., alias="schema")
    database: str
    columns: list[str]


class DashboardOwner(BaseModel):
    user_id: str  #  Typically an email or a uuid.
    username: (
        str | None
    )  # Typically an email address. Empty in PBI if a group or app is the owner.
    name: str  # Typically the human name.


class Dashboard(BaseModel):
    external_id: str
    url: str
    type: Literal["powerbi", "qliksense"]
    name: str
    workspace: str
    created_at: datetime | None
    modified_at: datetime
    owners: list[DashboardOwner]
    parent_models: list[DataModel]


class DashboardSchemaMetadata(BaseModel):
    schema_field: str = Field(..., alias="schema")
    version: int


class DashboardManifest(BaseModel):
    metadata: DashboardSchemaMetadata
    payload: list[Dashboard]
