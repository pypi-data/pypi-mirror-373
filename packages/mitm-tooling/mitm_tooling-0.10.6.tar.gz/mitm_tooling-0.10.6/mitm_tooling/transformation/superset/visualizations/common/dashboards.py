from collections.abc import Collection

from mitm_tooling.representation.intermediate import HeaderEntry

from ...definitions import (
    DashboardIdentifier,
    DatasetIdentifierMap,
    SupersetDashboardDef,
)
from ...factories.dashboard import mk_dashboard_def
from ..abstract import ChartCollectionCreator, ChartDefCollection, MitMDashboardCreator
from .chart_collections import HeaderMetaTablesCollection


class MitMBaselineDashboard(MitMDashboardCreator):
    @property
    def chart_collection_creator(self) -> ChartCollectionCreator:
        return ChartCollectionCreator.prefixed(
            'mitm-baseline', HeaderMetaTablesCollection(self.header, self.sql_rep_schema)
        )

    @property
    def dashboard_title(self) -> str:
        name = self.mitm_dataset_identifier.dataset_name
        return 'MITM Dashboard' + (f' ({name})' if name else ' (anonymous)')

    def build_dashboard(
        self,
        ds_id_map: DatasetIdentifierMap,
        chart_collection: ChartDefCollection,
        dashboard_identifier: DashboardIdentifier,
    ) -> SupersetDashboardDef:
        from ...factories.dashboard_constructors import CHART, DASH, ROW, TABS

        def tabs(hes: Collection[HeaderEntry]):
            res = {}
            for he in hes:
                t = he.type_name
                res[f'{he.kind}: {t}'] = [
                    ROW(CHART(chart_collection[f'mitm-baseline-{he.concept}-{t}-attributes-table'], 4, 25))
                ]
            return res

        dashboard = DASH(
            dashboard_identifier.dashboard_title,
            ROW(
                CHART(chart_collection['mitm-baseline-header-counts-table'], 6, 50),
                CHART(chart_collection['mitm-baseline-header-types-table'], 6, 50),
            ),
            *(TABS(tabs(ts.values())) for c, ts in self.header.as_dict.items()),
        )

        return mk_dashboard_def(
            dashboard_identifier.dashboard_title,
            position_data=dashboard(),
            description='A rudimentary dashboard to view MITM data.',
            uuid=dashboard_identifier.uuid,
        )
