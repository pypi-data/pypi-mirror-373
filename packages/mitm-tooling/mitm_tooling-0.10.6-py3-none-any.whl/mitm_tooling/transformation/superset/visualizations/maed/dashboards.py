from mitm_tooling.representation.intermediate import Header, HeaderEntry

from ...definitions import (
    ControlValues,
    DashboardIdentifier,
    DatasetIdentifierMap,
    FilterType,
    NativeFilterConfig,
    SupersetDashboardDef,
)
from ...factories.dashboard import mk_dashboard_def, mk_filter_config
from ..abstract import ChartCollectionCreator, ChartDefCollection, MitMDashboardCreator
from .chart_collections import BaselineMAEDCharts, ExperimentalMAEDCharts, MAEDCustomChart


def mk_header_markdown(header: Header) -> tuple[str, str]:
    cols = 2 + header.max_k  # Concept, Type, Attr_1..Attr_k
    headers = ['Concept', 'Type'] + [f'Attr_{i}' for i in range(1, header.max_k + 1)]
    separator = ['---'] * cols

    # Header row
    lines = [
        '# Header',
        '| ' + ' | '.join(headers) + ' |',
        '| ' + ' | '.join(separator) + ' |',
    ]

    # Data rows
    for he in header.header_entries:
        row = [he.kind, he.type_name]
        for a, dt in he.iter_attr_dtype_pairs():
            row.append(f'{a} (_{dt}_)')
        row.extend([''] * (cols - len(row)))
        assert len(row) == cols
        lines.append('| ' + ' | '.join(row) + ' |')

    table_txt = '\n'.join(lines) + '\n'

    summary_txt = (
        f'**MitM**: {header.mitm}'
        + '\n'
        + '\n'.join((r'- \# types: ' + str(len(hes)) for c, hes in header.as_dict.items()))
        + '\n'
    )

    return summary_txt, table_txt


def mk_maed_filters(ds_id_map: DatasetIdentifierMap) -> list[NativeFilterConfig]:
    return [
        mk_filter_config(
            'Object',
            targets=[('object', ds_id_map['observations'].uuid)],
            filter_type=FilterType.FILTER_SELECT,
            control_values=ControlValues(multiSelect=True, searchAllOptions=False, inverseSelection=False),
        ),
        mk_filter_config(
            'Time Grain',
            targets=[ds_id_map['observations'].uuid],
            filter_type=FilterType.FILTER_TIME_GRAIN,
        ),
        mk_filter_config(
            'Time Range',
            filter_type=FilterType.FILTER_TIME,
        ),
    ]


class BaselineMAEDDashboard(MitMDashboardCreator):
    @property
    def chart_collection_creator(self) -> ChartCollectionCreator:
        return ChartCollectionCreator.prefixed('maed-baseline', BaselineMAEDCharts(self.header, self.sql_rep_schema))

    @property
    def dashboard_title(self) -> str:
        name = self.mitm_dataset_identifier.dataset_name
        return 'MAED Dashboard' + (f' ({name})' if name else ' (anonymous)')

    def build_dashboard(
        self,
        ds_id_map: DatasetIdentifierMap,
        chart_collection: ChartDefCollection,
        dashboard_identifier: DashboardIdentifier,
    ) -> SupersetDashboardDef:
        filters = mk_maed_filters(ds_id_map)

        from ...factories.dashboard_constructors import CHART, DASH, ROW

        dashboard = DASH(
            dashboard_identifier.dashboard_title,
            ROW(
                CHART(chart_collection['maed-baseline-observation-objects-pie'], 4, 50),
                CHART(chart_collection['maed-baseline-event-count-ts'], 4, 50),
                CHART(chart_collection['maed-baseline-measurement-count-ts'], 4, 50),
            ),
            *(
                ROW(CHART(chart_collection[f'maed-baseline-measurement-{he.type_name}-ts'], 12, 50))
                for he in self.header.as_dict.get('measurement', {}).values()
            ),
            *(
                ROW(CHART(chart_collection[f'maed-baseline-event-{he.type_name}-count-ts'], 12, 50))
                for he in self.header.as_dict.get('event', {}).values()
            ),
            ROW(CHART(chart_collection['maed-baseline-event-horizon'], 12, 50)),
        )

        return mk_dashboard_def(
            dashboard_identifier.dashboard_title,
            position_data=dashboard(),
            description='A rudimentary dashboard to view MAED data.',
            native_filters=filters,
            uuid=dashboard_identifier.uuid,
        )


class ExperimentalMAEDDashboard(MitMDashboardCreator):
    @property
    def chart_collection_creator(self) -> ChartCollectionCreator:
        return ChartCollectionCreator.prefixed(
            'maed-experimental',
            ChartCollectionCreator.union(
                BaselineMAEDCharts(self.header, self.sql_rep_schema),
                ExperimentalMAEDCharts(self.header, self.sql_rep_schema),
            ),
        )

    @property
    def dashboard_title(self) -> str:
        name = self.mitm_dataset_identifier.dataset_name
        return 'Experimental MAED Dashboard' + (f' ({name})' if name else ' (anonymous)')

    def build_dashboard(
        self,
        ds_id_map: DatasetIdentifierMap,
        chart_collection: ChartDefCollection,
        dashboard_identifier: DashboardIdentifier,
    ) -> SupersetDashboardDef:
        filters = mk_maed_filters(ds_id_map)

        from ...factories.dashboard_constructors import CHART, COLS, DASH, HEADER, ROW, TABS

        def obs_tabs(hes: list[HeaderEntry], counts: bool = False):
            res = {}
            for he in hes:
                t = he.type_name
                res[f'{he.kind}: {t}'] = [
                    ROW(
                        CHART(chart_collection[f'maed-experimental-{he.concept}-{t}-instance-counts'], 4, 25),
                        CHART(chart_collection[f'maed-experimental-{he.concept}-{t}-attributes-table'], 4, 25),
                    ),
                    CHART(
                        chart_collection[f'maed-experimental-{he.concept}-{t}{"-count" if counts else ""}-ts'], 12, 50
                    ),
                ]
            return res

        header_line_txt = f'MAED // Dataset: {self.mitm_dataset_identifier.dataset_name or "Unnamed"}'
        dashboard = DASH(
            dashboard_identifier.dashboard_title,
            ROW(COLS((4, [HEADER(header_line_txt)]))),
            ROW(
                CHART(chart_collection['maed-experimental-header-counts-table'], 6, 50),
                CHART(chart_collection['maed-experimental-header-types-table'], 6, 50),
            ),
            ROW(
                CHART(chart_collection['maed-experimental-observation-objects-pie'], 4, 50),
                CHART(chart_collection['maed-experimental-event-count-ts'], 4, 50),
                CHART(chart_collection['maed-experimental-measurement-count-ts'], 4, 50),
            ),
            TABS(obs_tabs(self.header.as_dict.get('measurement', {}).values())),
            TABS(obs_tabs(self.header.as_dict.get('event', {}).values(), counts=True)),
            ROW(CHART(chart_collection['maed-experimental-event-horizon'], 12, 50)),
        )

        return mk_dashboard_def(
            dashboard_identifier.dashboard_title,
            position_data=dashboard(),
            description='An experimental dashboard to view MAED data.',
            native_filters=filters,
            uuid=dashboard_identifier.uuid,
        )


class CustomChartMAEDDashboard(MitMDashboardCreator):
    @property
    def dashboard_title(self) -> str:
        name = self.mitm_dataset_identifier.dataset_name
        return 'Custom Chart MAED Dashboard' + (f' ({name})' if name else ' (anonymous)')

    @property
    def chart_collection_creator(self) -> ChartCollectionCreator:
        mitm_dataset_identifier = self.mitm_dataset_identifier
        return ChartCollectionCreator.cls_from_dict(
            {'maed-custom': ('segments', MAEDCustomChart(mitm_dataset_identifier))}
        )()

    def build_dashboard(
        self,
        ds_id_map: DatasetIdentifierMap,
        chart_collection: ChartDefCollection,
        dashboard_identifier: DashboardIdentifier,
    ) -> SupersetDashboardDef:
        from mitm_tooling.transformation.superset.factories.dashboard_constructors import CHART, DASH, ROW

        dashboard = DASH(dashboard_identifier.dashboard_title, ROW(CHART(chart_collection['maed-custom'], 12, 400)))

        return mk_dashboard_def(
            dashboard_identifier.dashboard_title,
            position_data=dashboard(),
            description='An experimental dashboard to view MAED data.',
            uuid=dashboard_identifier.uuid,
        )
