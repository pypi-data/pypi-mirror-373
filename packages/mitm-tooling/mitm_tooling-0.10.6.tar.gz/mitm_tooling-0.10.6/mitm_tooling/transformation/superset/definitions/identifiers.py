import pydantic

from mitm_tooling.representation.sql import TableName
from mitm_tooling.utilities.identifiers import mk_uuid

from .constants import BaseSupersetDefinition, StrUUID, SupersetId


class SupersetObjectIdentifier(BaseSupersetDefinition):
    id: SupersetId | None = None
    uuid: StrUUID = pydantic.Field(default_factory=mk_uuid)


class DatabaseIdentifier(SupersetObjectIdentifier):
    database_name: str | None = None


class DatasetIdentifier(SupersetObjectIdentifier):
    table_name: str | None = None


DatasetIdentifierMap = dict[TableName, DatasetIdentifier]


class ChartIdentifier(SupersetObjectIdentifier):
    slice_name: str | None = None


ChartIdentifierMap = dict[str, ChartIdentifier]


class DashboardIdentifier(SupersetObjectIdentifier):
    dashboard_title: str | None = None


DashboardIdentifierMap = dict[str, DashboardIdentifier]
DashboardGroupsIdentifierMap = dict[str, DashboardIdentifierMap]


class MitMDatasetIdentifier(SupersetObjectIdentifier):
    dataset_name: str | None = None
