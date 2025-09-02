from mitm_tooling.representation.intermediate import Header
from mitm_tooling.representation.sql import SQLRepresentationSchema, TableName, mk_sql_rep_schema

from ...asset_bundles import NamedChartIdentifierMap
from ...definitions import (
    ChartIdentifier,
    ChartIdentifierMap,
    DatasetIdentifier,
    DatasetIdentifierMap,
    MitMDatasetIdentifier,
    SupersetChartDef,
)
from ...factories.custom_charts import mk_maed_custom_chart
from ..abstract import ChartCollectionCreator, ChartCreator, ChartDefCollection
from ..common.chart_collections import HeaderMetaTablesCollection, per_type_charts, per_type_with_header_charts
from .charts import (
    MAEDConceptCountTS,
    MAEDInstanceCountBigNumber,
    MAEDInstanceCountsHorizon,
    MAEDNumericAttributesTS,
    MAEDRelationPie,
    MAEDTypeAvgCountTS,
)

MAEDTypesAvgCountTSCollection = per_type_charts('count-ts', lambda c, t: MAEDTypeAvgCountTS(c, t))
MAEDInstanceCountsCollection = per_type_charts('instance-counts', lambda c, t: MAEDInstanceCountBigNumber(c, t))
MAEDAverageAttributesTSCollection = per_type_with_header_charts('ts', lambda he: MAEDNumericAttributesTS(he))


class BaselineMAEDCharts(ChartCollectionCreator):
    def __init__(self, header: Header, sql_rep_schema: SQLRepresentationSchema | None = None):
        super().__init__()
        self.header = header
        self.sql_rep_schema = sql_rep_schema or mk_sql_rep_schema(header)
        self.mitm_def = header.mitm_def

    @property
    def chart_creators(self) -> dict[str, tuple[TableName, ChartCreator]]:
        ccs = {}
        observation_table_name = self.sql_rep_schema.concept_tables['observation'].name
        for sub_concept in self.mitm_def.sub_concept_map['observation']:
            ccs[f'{sub_concept}-count-ts'] = (observation_table_name, MAEDConceptCountTS(sub_concept))
        ccs['observation-objects-pie'] = (observation_table_name, MAEDRelationPie('observation', 'object'))
        ccs['event-horizon'] = (self.sql_rep_schema.view_tables['events_view'].name, MAEDInstanceCountsHorizon('event'))
        return ccs

    def mk_chart_collection(self, ds_id_map: DatasetIdentifierMap, ch_id_map: ChartIdentifierMap) -> ChartDefCollection:
        charts = super().mk_chart_collection(ds_id_map, ch_id_map)
        charts.update(
            MAEDInstanceCountsCollection(['event', 'measurement'], self.sql_rep_schema).mk_chart_collection(
                ds_id_map, ch_id_map
            )
        )
        charts.update(
            MAEDTypesAvgCountTSCollection(['event'], self.sql_rep_schema).mk_chart_collection(ds_id_map, ch_id_map)
        )
        charts.update(
            MAEDAverageAttributesTSCollection(['measurement'], self.header, self.sql_rep_schema).mk_chart_collection(
                ds_id_map, ch_id_map
            )
        )
        return charts


class ExperimentalMAEDCharts(ChartCollectionCreator):
    def __init__(self, header: Header, sql_rep_schema: SQLRepresentationSchema | None = None):
        super().__init__()
        self.header = header
        self.sql_rep_schema = sql_rep_schema or mk_sql_rep_schema(header)
        self.mitm_def = header.mitm_def

    @property
    def chart_creators(self) -> dict[str, tuple[TableName, ChartCreator]]:
        return {}

    def mk_chart_collection(
        self, ds_id_map: DatasetIdentifierMap, ch_id_map: NamedChartIdentifierMap
    ) -> ChartDefCollection:
        return ChartCollectionCreator.union(
            HeaderMetaTablesCollection(self.header, self.sql_rep_schema)
        ).mk_chart_collection(ds_id_map, ch_id_map)


class MAEDCustomChart(ChartCreator):
    def __init__(self, mdi: MitMDatasetIdentifier):
        self.mdi = mdi

    @property
    def slice_name(self) -> str:
        return 'Custom MAED Chart'

    def build_chart(self, dataset_identifier: DatasetIdentifier, chart_identifier: ChartIdentifier) -> SupersetChartDef:
        return mk_maed_custom_chart(
            chart_identifier.slice_name, self.mdi, dataset_identifier, uuid=chart_identifier.uuid
        )
