from mitm_tooling.definition import MITM
from mitm_tooling.representation.intermediate import Header
from mitm_tooling.utilities.identifiers import name_plus_uuid

from .constants import StrUUID, SupersetDefFile
from .core import SupersetObjectMixin
from .identifiers import ChartIdentifier, DashboardIdentifier, DatasetIdentifier, MitMDatasetIdentifier

RelatedTable = DatasetIdentifier
RelatedSlice = ChartIdentifier
RelatedDashboard = DashboardIdentifier


class SupersetMitMDatasetDef(SupersetObjectMixin, SupersetDefFile):
    uuid: StrUUID
    dataset_name: str
    mitm: MITM
    mitm_header: Header | None = None
    database_uuid: StrUUID
    tables: list[RelatedTable] | None = None
    slices: list[RelatedSlice] | None = None
    dashboards: list[RelatedDashboard] | None = None
    version: str = '1.0.0'

    @property
    def identifier(self) -> MitMDatasetIdentifier:
        return MitMDatasetIdentifier(uuid=self.uuid, dataset_name=self.dataset_name, id=-1)

    @property
    def filename(self) -> str:
        return name_plus_uuid(self.dataset_name, self.uuid, sep='_')
