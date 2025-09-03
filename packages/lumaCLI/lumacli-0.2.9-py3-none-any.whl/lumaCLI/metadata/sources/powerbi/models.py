from enum import Enum
from typing import Any

from pydantic import BaseModel, EmailStr


class ColumnType(str, Enum):
    CalculatedTableColumn = "CalculatedTableColumn"
    Calculated = "Calculated"
    Data = "Data"


class TableColumn(BaseModel):
    name: str
    dataType: str
    isHidden: bool
    columnType: ColumnType


class TableMeasure(BaseModel):
    name: str
    expression: str
    description: str | None = None
    isHidden: bool


class TableSource(BaseModel):
    expression: str


class Table(BaseModel):
    name: str
    isHidden: bool
    columns: list[TableColumn] = []
    measures: list[TableMeasure] = []
    source: list[TableSource] | None = None


class Dataset(BaseModel):
    id: str
    name: str
    tables: list[Table] = []
    description: str | None = None
    configuredBy: EmailStr | None = None
    configuredById: str | None = None
    directQueryRefreshSchedule: dict[str, Any] | None = None
    createdDate: str
    users: list[dict] | None = None


class DashboardTile(BaseModel):
    id: str
    title: str
    reportId: str
    datasetId: str


class Dashboard(BaseModel):
    id: str
    displayName: str
    tiles: list[DashboardTile]
    users: list[dict]
    tags: list[str]


class ReportUser(BaseModel):
    reportUserAccessRight: str
    emailAddress: EmailStr | None
    displayName: str
    identifier: EmailStr | str
    graphId: str
    principalType: str
    userType: str | None


class Report(BaseModel):
    id: str
    appId: str | None = None
    name: str
    datasetId: str
    description: str | None = None
    createdDateTime: str | None = None
    modifiedDateTime: str | None = None
    users: list[ReportUser]


class Workspace(BaseModel):
    id: str
    name: str
    type: str = "Workspace"
    state: str
    reports: list[Report] = []
    datasets: list[Dataset] = []
    dashboards: list[Dashboard] = []
    users: list[dict]


class WorkspaceInfo(BaseModel):
    workspaces: list[Workspace]
    datasourceInstances: list[dict] | None = None
