"""Pydantic models for dbt objects."""

from datetime import datetime
from typing import Literal, Optional, Union

from pydantic import BaseModel, Field


class DBTMetadata(BaseModel):
    dbt_version: Optional[str]
    dbt_schema_version: Optional[str]
    generated_at: Optional[str]
    adapter_type: Optional[str]
    dbt_env: Optional[dict]
    invocation_id: Optional[str]
    send_anonymous_usage_stats: Optional[bool]
    project_id: Optional[str]
    user_id: Optional[str]


Meta = dict[str, Union[str, int, float, bool, list[str], list[dict]]]


class Column(BaseModel):
    name: Optional[str]
    description: Optional[str]
    meta: Meta = {}
    data_type: Optional[str]
    quote: Optional[str]
    tags: Optional[list[str]]


class Macro(BaseModel):
    # Common.
    name: Optional[str] = Field(description="Name of the object")
    unique_id: Optional[str]
    package_name: Optional[str]
    root_path: Optional[str]
    path: Optional[str]
    original_file_path: Optional[str]

    # Important.
    resource_type: Optional[Literal["macro"]]
    meta: Meta = {}
    description: Optional[str]
    tags: Optional[list]

    # Other.
    macro_sql: Optional[str]
    depends_on: Optional[dict]
    docs: Optional[dict]
    patch_path: Optional[str]
    arguments: Optional[list]
    created_at: Optional[float]


class Doc(BaseModel):
    __tablename__: str = "docs"

    # Common.
    name: Optional[str] = Field(description="Name of the object")
    unique_id: Optional[str]
    package_name: Optional[str]
    root_path: Optional[str]
    path: Optional[str]
    original_file_path: Optional[str]

    # Other.
    block_contents: Optional[str]


class Exposure(BaseModel):
    __tablename__: str = "exposure"

    # Common.
    name: Optional[str] = Field(description="Name of the object")
    unique_id: Optional[str]
    package_name: Optional[str]
    root_path: Optional[str]
    path: Optional[str]
    original_file_path: Optional[str]


class Metrics(BaseModel):
    __tablename__: str = "metric"

    # Common.
    name: Optional[str] = Field(description="Name of the object")
    unique_id: Optional[str]
    package_name: Optional[str]
    root_path: Optional[str]
    path: Optional[str]
    original_file_path: Optional[str]


class SourceBase(BaseModel):
    __tablename__: str = "sources"

    # Common.
    name: Optional[str] = Field(description="Name of the object")
    unique_id: Optional[str]
    package_name: Optional[str]
    root_path: Optional[str]
    path: Optional[str]
    original_file_path: Optional[str]

    # Important.
    resource_type: Optional[str]
    relation_name: Optional[str]
    description: Optional[str]
    loaded_at_field: Optional[str]

    # Other.
    schema_field: Optional[str] = Field(alias="schema")
    source_name: Optional[str]
    source_description: Optional[str]
    loader: Optional[str]
    identifier: Optional[str]
    created_at: Optional[float]


class Source(SourceBase):
    meta: Meta = {}  # noqa: RUF012
    columns: Optional[dict[str, Column]]
    resource_type: Optional[Literal["source"]]
    tags: Optional[list]
    freshness: Optional[dict]
    database: Optional[str]
    fqn: Optional[list]
    quoting: Optional[dict]
    external: Optional[dict]
    source_meta: Optional[dict]
    config: Optional[dict]
    patch_path: Optional[dict]
    unrendered_config: Optional[dict]


class Node(BaseModel):
    """Fields common to every Node (models, seeds, tests)."""

    compiled: Optional[bool]
    database: Optional[str]
    schema_field: Optional[str] = Field(alias="schema")
    fqn: Optional[list]
    unique_id: str
    raw_code: Optional[str]
    language: Optional[str]
    package_name: str
    root_path: Optional[str]
    path: str
    original_file_path: str
    name: str
    resource_type: str
    alias: str
    checksum: dict
    config: Optional[dict]
    tags: Optional[list]
    refs: Optional[list]
    sources: Optional[dict]
    metrics: Optional[dict]
    depends_on: Optional[dict]
    description: Optional[str]
    columns: Optional[dict[str, Column]]
    meta: Meta = {}
    docs: Optional[dict]
    patch_path: Optional[str]
    compiled_path: Optional[str]
    build_path: Optional[str]
    deferred: Optional[bool]
    unrendered_config: Optional[dict]
    created_at: Optional[float]
    config_call_dict: Optional[dict]
    compiled_code: Optional[str]
    extra_ctes_injected: Optional[bool]
    extra_ctes: Optional[dict]
    relation_name: Optional[str]
    catalog_created_at: Optional[datetime]
    catalog_updated_at: Optional[datetime]


class Model(Node):
    pass


class Seed(Node):
    pass


class Test(Node):
    pass


class DBTManifest(BaseModel):
    dbt_metadata: Optional[DBTMetadata] = Field(alias="metadata")
    nodes: Optional[dict[str, Node]]
    sources: Optional[dict[str, Source]]
    macros: Optional[dict[str, Macro]]
    docs: Optional[dict[str, Doc]]
    exposures: Optional[dict[str, Exposure]]
    metrics: Optional[dict[str, Metrics]]
    selectors: Optional[dict[str, str]]
    disabled: Optional[dict]
    parent_map: Optional[dict[str, list[Optional[str]]]]
    child_map: Optional[dict[str, list[Optional[str]]]]


class CatalogNodeMetadata(BaseModel):
    type: str
    schema_field: str | None = Field(..., alias="schema")
    name: str
    database: Optional[str]
    comment: Optional[str]
    owner: Optional[str]


class CatalogNodeColumns(BaseModel):
    type: Optional[str]
    index: int
    name: Optional[str]
    comment: Optional[str]


class CatalogNodeStats(BaseModel):
    id: Optional[str]
    label: Optional[str]
    value: Optional[Union[bool, str, float]]
    include: Optional[bool]
    description: Optional[str]


class CatalogNodes(BaseModel):
    dbt_metadata: CatalogNodeMetadata = Field(alias="metadata")
    columns: dict[str, CatalogNodeColumns]
    stats: CatalogNodeStats
    unique_id: Optional[str]


class CatalogSource(CatalogNodes):
    pass


class DBTCatalog(BaseModel):
    dbt_metadata: DBTMetadata = Field(alias="metadata")
    nodes: dict[str, CatalogNodes]
    sources: dict[str, CatalogSource]
    errors: Optional[str]


class RunResultsTimingInfo(BaseModel):
    name: str
    started_at: Optional[str]
    completed_at: Optional[str]


class RunResultsResults(BaseModel):
    status: str
    timing: list[RunResultsTimingInfo]
    thread_id: str
    execution_time: float
    adapter_response: dict
    message: Optional[str]
    failures: Optional[int]
    unique_id: str


class RunResultsDict(BaseModel):
    dbt_metadata: DBTMetadata = Field(alias="metadata")
    results: list[dict]
    elapsed_time: float
    args: Optional[dict]


class SourcesFreshnessRuntimeError(BaseModel):
    unique_id: str
    error: Optional[Union[str, int]]
    status: str


class SourceFreshnessThresholdWarnAfter(BaseModel):
    count: Optional[int]
    period: Optional[str]


class SourceFreshnessThresholdErrorAfter(SourceFreshnessThresholdWarnAfter):
    pass


class SourceFreshnessThreshold(BaseModel):
    warn_after: Optional[SourceFreshnessThresholdWarnAfter]
    error_after: Optional[SourceFreshnessThresholdErrorAfter]
    filter: Optional[str]


class SourcesTimingInfo(RunResultsTimingInfo):
    pass


class SourcesFreshnessOutput(BaseModel):
    unique_id: str
    max_loaded_at: str
    snapshotted_at: str
    max_loaded_at_time_ago_in_s: float
    status: str
    criteria: SourceFreshnessThreshold
    adapter_response: dict
    timing: SourcesTimingInfo
    thread_id: str
    execution_time: float


class DBTSources(BaseModel):
    dbt_metadata: DBTMetadata = Field(alias="metadata")
    results: list[Union[SourcesFreshnessRuntimeError, SourcesFreshnessOutput]]
    elapsed_time: float
