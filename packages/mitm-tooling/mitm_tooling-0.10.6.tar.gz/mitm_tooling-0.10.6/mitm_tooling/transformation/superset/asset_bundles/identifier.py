from typing import Self
from uuid import UUID

import pydantic

from mitm_tooling.utilities.python_utils import deep_merge_dicts

from ..definitions import (
    BaseSupersetDefinition,
    ChartIdentifierMap,
    DashboardIdentifierMap,
    DatabaseIdentifier,
    DatasetIdentifierMap,
    MitMDatasetIdentifier,
    SupersetMitMDatasetDef,
)

NamedDashboardIdentifierMap = DashboardIdentifierMap
VizCollectionIdentifierMap = dict[str, NamedDashboardIdentifierMap]
NamedChartIdentifierMap = ChartIdentifierMap


class DatasourceIdentifierBundle(BaseSupersetDefinition):
    database: DatabaseIdentifier | None = None
    ds_id_map: DatasetIdentifierMap = pydantic.Field(default_factory=dict)

    @property
    def database_uuid(self) -> UUID | None:
        if self.database is not None:
            return self.database.uuid
        return None

    @classmethod
    def from_mitm_dataset(cls, mitm_dataset: SupersetMitMDatasetDef) -> Self:
        return cls(
            database=DatabaseIdentifier(uuid=mitm_dataset.database_uuid),
            ds_id_map={t.table_name: t for t in (mitm_dataset.tables or [])},
        )


class VisualizationsIdentifierBundle(BaseSupersetDefinition):
    ch_id_map: NamedChartIdentifierMap = pydantic.Field(default_factory=dict)
    viz_id_map: VizCollectionIdentifierMap = pydantic.Field(default_factory=dict)


class MitMDatasetIdentifierBundle(DatasourceIdentifierBundle, VisualizationsIdentifierBundle):
    mitm_dataset: MitMDatasetIdentifier | None = None

    @property
    def mitm_dataset_uuid(self) -> UUID | None:
        if self.mitm_dataset is not None:
            return self.mitm_dataset.uuid
        return None

    @classmethod
    def from_mitm_dataset(cls, mitm_dataset: SupersetMitMDatasetDef) -> Self:
        return cls(
            mitm_dataset=mitm_dataset.identifier,
            database=DatabaseIdentifier(uuid=mitm_dataset.database_uuid),
            ds_id_map={t.table_name: t for t in (mitm_dataset.tables or [])},
            ch_id_map={ch.slice_name: ch for ch in (mitm_dataset.slices or [])},
            viz_id_map={'default': {dash.dashboard_title: dash for dash in (mitm_dataset.dashboards or [])}},
        )

    def with_visualizations(self, *viz_id_bundles: VisualizationsIdentifierBundle) -> Self:
        merged_ch_id_map = deep_merge_dicts(self.ch_id_map, *(id_bundle.ch_id_map for id_bundle in viz_id_bundles))
        merged_viz_id_map = deep_merge_dicts(self.viz_id_map, *(id_bundle.viz_id_map for id_bundle in viz_id_bundles))
        return self.model_copy(update=dict(ch_id_map=merged_ch_id_map, viz_id_map=merged_viz_id_map), deep=True)
