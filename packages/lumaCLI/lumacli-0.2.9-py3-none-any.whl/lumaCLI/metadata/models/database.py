from pydantic import BaseModel, Field


class DatabaseTableColumn(BaseModel):
    name: str
    type: str
    length: str
    description: str | None


class DatabaseTable(BaseModel):
    type: str
    name: str
    columns: list[DatabaseTableColumn]


class DatabaseTableSchemaMetadata(BaseModel):
    schema_field: str = Field(..., alias="schema")
    version: int


class DatabaseTableManifest(BaseModel):
    metadata: DatabaseTableSchemaMetadata
    payload: list[DatabaseTable]
