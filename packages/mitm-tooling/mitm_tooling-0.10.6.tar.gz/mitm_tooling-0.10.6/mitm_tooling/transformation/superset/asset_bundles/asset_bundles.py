import itertools
from abc import ABC, abstractmethod
from typing import Any, Self
from uuid import UUID

import pydantic

from mitm_tooling.representation.sql import TableName
from mitm_tooling.utilities.python_utils import deep_merge_dicts

from ..definitions import (
    ChartIdentifierMap,
    DashboardIdentifierMap,
    DatabaseIdentifier,
    DatasetIdentifier,
    DatasetIdentifierMap,
    MetadataType,
    SupersetAssetsImport,
    SupersetChartDef,
    SupersetDashboardDef,
    SupersetDatabaseDef,
    SupersetDatasetDef,
    SupersetDefFolder,
    SupersetMitMDatasetDef,
    SupersetMitMDatasetImport,
)
from ..factories.importable import mk_assets_import, mk_mitm_dataset_import
from .identifier import (
    DatasourceIdentifierBundle,
    MitMDatasetIdentifierBundle,
    NamedChartIdentifierMap,
    VisualizationsIdentifierBundle,
    VizCollectionIdentifierMap,
)


class SupersetAssetBundle(SupersetDefFolder, ABC):
    @abstractmethod
    def to_import(self) -> SupersetAssetsImport | SupersetMitMDatasetImport:
        pass

    @property
    def folder_dict(self) -> dict[str, Any]:
        return self.to_import().folder_dict


class SupersetDatasourceBundle(SupersetAssetBundle):
    database: SupersetDatabaseDef
    datasets: list[SupersetDatasetDef] = pydantic.Field(default_factory=list)

    @property
    def database_uuid(self) -> UUID:
        return self.database.uuid

    @property
    def dataset_uuids(self) -> list[UUID]:
        return [ds.uuid for ds in self.datasets]

    @property
    def database_identifier(self) -> DatabaseIdentifier:
        return self.database.identifier

    @property
    def dataset_identifier_map(self) -> DatasetIdentifierMap:
        return {ds.table_name: ds.identifier for ds in self.datasets}

    @property
    def identifiers(self) -> DatasourceIdentifierBundle:
        return DatasourceIdentifierBundle(database=self.database_identifier, ds_id_map=self.dataset_identifier_map)

    @property
    def placeholder_dataset_identifiers(self) -> dict[TableName, DatasetIdentifier]:
        return {ds.table_name: DatasetIdentifier(uuid=ds.uuid, id=-1) for ds in self.datasets}

    def to_import(self, metadata_type: MetadataType = MetadataType.Assets) -> SupersetAssetsImport:
        return mk_assets_import(databases=[self.database], datasets=self.datasets, metadata_type=metadata_type)


class SupersetVisualizationBundle(SupersetAssetBundle):
    charts: list[SupersetChartDef] = pydantic.Field(default_factory=list)
    dashboards: list[SupersetDashboardDef] = pydantic.Field(default_factory=list)
    named_charts: NamedChartIdentifierMap | None = None
    viz_collections: VizCollectionIdentifierMap | None = None

    @property
    def identifiers(self) -> VisualizationsIdentifierBundle:
        return VisualizationsIdentifierBundle(ch_id_map=self.named_charts_map, viz_id_map=self.viz_identifier_map)

    @property
    def chart_uuids(self) -> list[UUID]:
        return [ch.uuid for ch in self.charts]

    @property
    def dashboard_uuids(self) -> list[UUID]:
        return [da.uuid for da in self.dashboards]

    @property
    def chart_identifier_map(self) -> ChartIdentifierMap:
        return {ch.slice_name: ch.identifier for ch in self.charts}

    @property
    def dashboard_identifier_map(self) -> DashboardIdentifierMap:
        return {da.dashboard_title: da.identifier for da in self.dashboards}

    @property
    def named_charts_map(self) -> NamedChartIdentifierMap:
        if self.named_charts is None:
            return self.chart_identifier_map
        else:
            return self.named_charts

    @property
    def viz_identifier_map(self) -> VizCollectionIdentifierMap:
        if self.viz_collections is None:
            return {'default': self.dashboard_identifier_map}
        else:
            return self.viz_collections

    def take_viz(self, viz_name: str) -> Self | None:
        # the charts are not filtered
        if coll := self.viz_identifier_map.get(viz_name):
            uuids = {di.uuid for di in coll.values()}
            dashes = [dash for dash in self.dashboards if dash.uuid in uuids]
            return self.__class__(
                charts=list(self.charts),
                dashboards=dashes,
                named_charts=dict(self.named_charts),
                viz_collections={viz_name: coll},
            )
        else:
            return None

    @classmethod
    def combine(cls, *bundles: Self) -> Self:
        if not bundles or len(bundles) == 0:
            return cls()

        charts, dashboards = (
            itertools.chain(*(b.charts for b in bundles)),
            itertools.chain(*(b.dashboards for b in bundles)),
        )
        named_charts_map = deep_merge_dicts(*(b.named_charts_map for b in bundles))
        viz_collections_map = deep_merge_dicts(*(b.viz_identifier_map for b in bundles))

        return cls(
            charts=list(charts),
            dashboards=list(dashboards),
            named_charts=named_charts_map,
            viz_collections=viz_collections_map,
        )

    def to_import(self, metadata_type: MetadataType = MetadataType.Assets) -> SupersetAssetsImport:
        return mk_assets_import(charts=self.charts, dashboards=self.dashboards, metadata_type=metadata_type)


class SupersetMitMDatasetBundle(SupersetAssetBundle):
    mitm_dataset: SupersetMitMDatasetDef
    datasource_bundle: SupersetDatasourceBundle
    visualization_bundle: SupersetVisualizationBundle

    @property
    def identifiers(self) -> MitMDatasetIdentifierBundle:
        return MitMDatasetIdentifierBundle(
            mitm_dataset=self.mitm_dataset.identifier,
            database=self.datasource_bundle.database_identifier,
            ds_id_map=self.datasource_bundle.dataset_identifier_map,
            ch_id_map=self.visualization_bundle.named_charts_map,
            viz_id_map=self.visualization_bundle.viz_identifier_map,
        )

    def replace_visualization_bundle(self, visualization_bundle: SupersetVisualizationBundle) -> Self:
        mitm_ds = self.mitm_dataset
        from mitm_tooling.transformation.superset.factories.mitm_dataset import mk_mitm_dataset

        return self.__class__(
            mitm_dataset=mk_mitm_dataset(
                name=mitm_ds.dataset_name,
                mitm=mitm_ds.mitm,
                uuid=mitm_ds.uuid,
                header=mitm_ds.mitm_header,
                database_uuid=self.datasource_bundle.database_uuid,
                table_uuids=self.datasource_bundle.dataset_uuids,
                slice_uuids=visualization_bundle.chart_uuids,
                dashboard_uuids=visualization_bundle.dashboard_uuids,
            ),
            datasource_bundle=self.datasource_bundle,
            visualization_bundle=visualization_bundle,
        )

    def to_import(self, metadata_type: MetadataType = MetadataType.MitMDataset) -> SupersetMitMDatasetImport:
        base_assets = mk_assets_import(
            databases=[self.datasource_bundle.database],
            datasets=self.datasource_bundle.datasets,
            charts=self.visualization_bundle.charts,
            dashboards=self.visualization_bundle.dashboards,
            metadata_type=metadata_type,
        )
        return mk_mitm_dataset_import(
            mitm_datasets=[self.mitm_dataset], base_assets=base_assets, metadata_type=metadata_type
        )
