from collections.abc import Iterable
from uuid import UUID

from mitm_tooling.representation import ColumnName
from mitm_tooling.utilities.identifiers import mk_short_uuid_str, mk_uuid

from ..definitions import (
    BackgroundType,
    ChartMeta,
    ColName,
    ColumnMeta,
    ColumnOfDataset,
    ControlValues,
    DashboardChart,
    DashboardColumn,
    DashboardComponent,
    DashboardComponentType,
    DashboardDivider,
    DashboardGrid,
    DashboardHeader,
    DashboardInternalID,
    DashboardMarkdown,
    DashboardMetadata,
    DashboardPositionData,
    DashboardRoot,
    DashboardRow,
    DashboardTab,
    DashboardTabs,
    DatasetReference,
    FilterType,
    HeaderMeta,
    HeaderSize,
    MarkdownMeta,
    NativeFilterConfig,
    NativeFilterScope,
    SupersetChartDef,
    SupersetDashboardDef,
    TabMeta,
)

ComponentGrid = list[list[DashboardComponent]]


def mk_filter_config(
    name: str,
    targets: list[UUID | tuple[ColumnName, UUID]] | None = None,
    target_cols: list[tuple[ColumnName, UUID]] | None = None,
    target_datasets: list[UUID] | None = None,
    filter_type: FilterType = FilterType.FILTER_SELECT,
    control_values: ControlValues = ControlValues(),
    scope=NativeFilterScope(),
) -> NativeFilterConfig:
    def target_ref(x: UUID | tuple[ColumnName, UUID]) -> ColumnOfDataset | DatasetReference:
        return (
            ColumnOfDataset(column=ColName(name=x[0]), datasetUuid=x[1])
            if isinstance(x, tuple)
            else DatasetReference(datasetUuid=x)
        )

    if targets:
        targets = [target_ref(x) for x in targets]
    else:
        targets = [{}]  # stupid dummy value to avoid empty list
    return NativeFilterConfig(
        id=f'NATIVE_FILTER-{mk_short_uuid_str()}',
        name=name,
        filterType=filter_type,
        controlValues=control_values,
        targets=targets,
        scope=scope,
    )


def mk_dashboard_base(header_text: str, top_level_component_ids: list[DashboardInternalID]) -> DashboardPositionData:
    return {
        'DASHBOARD_VERSION_KEY': 'v2',
        'HEADER_ID': DashboardHeader(id='HEADER_ID', meta=HeaderMeta(text=header_text)),
        'ROOT_ID': DashboardRoot(id='ROOT_ID', children=['GRID_ID']),
        'GRID_ID': DashboardGrid(id='GRID_ID', children=top_level_component_ids),
    }


def mk_dashboard_header(
    text: str,
    header_size: HeaderSize = 'MEDIUM_HEADER',
    background: BackgroundType = 'BACKGROUND_TRANSPARENT',
    did: DashboardInternalID | None = None,
) -> DashboardHeader:
    return DashboardHeader(
        id=did or f'HEADER-{mk_short_uuid_str()}',
        meta=HeaderMeta(text=text, background=background, headerSize=header_size),
    )


def mk_dashboard_markdown(
    text: str | None = None, height: int = 50, width: int = 3, did: DashboardInternalID | None = None
) -> DashboardMarkdown:
    return DashboardMarkdown(
        id=did or f'MARKDOWN-{mk_short_uuid_str()}',
        meta=MarkdownMeta(height=height, width=width, code=(text if text else None)),
    )


def mk_dashboard_row(children_ids: list[DashboardInternalID], did: DashboardInternalID | None = None) -> DashboardRow:
    return DashboardRow(id=did or f'ROW-{mk_short_uuid_str()}', children=children_ids)


def mk_dashboard_column(
    children_ids: list[DashboardInternalID], width: int = 3, did: DashboardInternalID | None = None
) -> DashboardColumn:
    return DashboardColumn(
        id=did or f'COLUMN-{mk_short_uuid_str()}', children=children_ids, meta=ColumnMeta(width=width)
    )


def mk_dashboard_divider(did: DashboardInternalID | None = None) -> DashboardDivider:
    return DashboardDivider(id=did or f'DIVIDER-{mk_short_uuid_str()}')


def mk_dashboard_tab(
    text: str, children_ids: list[DashboardInternalID], did: DashboardInternalID | None = None
) -> DashboardTab:
    return DashboardTab(id=did or f'TAB-{mk_short_uuid_str()}', children=children_ids, meta=TabMeta(text=text))


def mk_dashboard_tabs(tab_ids: list[DashboardInternalID], did: DashboardInternalID | None = None) -> DashboardTabs:
    return DashboardTabs(id=did or f'TABS-{mk_short_uuid_str()}', children=tab_ids)


def mk_dashboard_chart(
    chart_uuid: UUID, width: int, height: int, slice_name: str | None = None, did: DashboardInternalID | None = None
) -> DashboardChart:
    return DashboardChart(
        id=did or f'CHART-{mk_short_uuid_str()}',
        meta=ChartMeta(uuid=chart_uuid, width=width, height=height, sliceName=slice_name),
    )


def mk_dashboard_position_data(
    header_text: str, top_level_comps: list[DashboardComponent], inner_components: list[DashboardComponent]
) -> DashboardPositionData:
    all_comps = top_level_comps + inner_components
    base: DashboardPositionData = mk_dashboard_base(
        header_text, top_level_component_ids=[c.id for c in top_level_comps]
    )
    return base | {c.id: c for c in all_comps}


def chart_to_def(chart_def: SupersetChartDef, width: int, height: int) -> DashboardChart:
    return mk_dashboard_chart(chart_uuid=chart_def.uuid, width=width, height=height)


def put_in_columns(
    components: Iterable[tuple[int, list[DashboardComponent]]],
) -> tuple[list[DashboardColumn], list[DashboardComponent]]:
    cols, elements = [], []
    for width, comps in components:
        elements.extend(comps)
        cols.append(mk_dashboard_column([comp.id for comp in elements], width=width))
    return cols, elements


def put_in_column_group(
    components: Iterable[tuple[int, list[DashboardComponent]]],
) -> tuple[DashboardRow, list[DashboardComponent]]:
    cols, elements = put_in_columns(components)
    row = mk_dashboard_row([col.id for col in cols])
    return row, elements


def put_in_rows(component_grid: ComponentGrid) -> tuple[list[DashboardRow], list[DashboardComponent]]:
    rows, elements = [], []
    for comps in component_grid:
        elements.extend(comps)
        rows.append(mk_dashboard_row([comp.id for comp in comps]))
    # elements.extend(rows)
    return rows, elements


def put_in_tabs(tabbed_components: dict[str, list[DashboardComponent]]) -> tuple[DashboardTabs, DashboardPositionData]:
    tabs, elements = [], []
    for text, comps in tabbed_components.items():
        elements.extend(comps)
        tabs.append(mk_dashboard_tab(text, [comp.id for comp in comps]))
    elements.extend(tabs)
    tabs_ = mk_dashboard_tabs([tab.id for tab in tabs])
    # elements.append(tabs_)
    return tabs_, elements


def mk_dashboard_position_data_legacy(header_text: str, comp_grid: ComponentGrid) -> DashboardPositionData:
    rows, elements = put_in_rows(comp_grid)
    position_base = mk_dashboard_base(header_text=header_text, top_level_component_ids=[r.id for r in rows])
    res = position_base | {r.id: r for r in rows} | {c.id: c for c in elements}
    return res


def mk_dashboard_metadata(native_filters: list[NativeFilterConfig] | None = None) -> DashboardMetadata:
    return DashboardMetadata(native_filter_configuration=native_filters or [])


def mk_dashboard_def(
    title: str,
    position_data: DashboardPositionData,
    native_filters: list[NativeFilterConfig] | None = None,
    description: str | None = None,
    uuid: UUID | None = None,
) -> SupersetDashboardDef:
    return SupersetDashboardDef(
        dashboard_title=title,
        position=position_data,
        metadata=(mk_dashboard_metadata(native_filters=native_filters)),
        description=description,
        uuid=uuid or mk_uuid(),
    )


def extract_charts(dashboard_def: SupersetDashboardDef) -> set[UUID]:
    return {
        c.meta.uuid
        for c in dashboard_def.position.values()
        if isinstance(c, DashboardComponent) and c.type == DashboardComponentType.CHART
    }
