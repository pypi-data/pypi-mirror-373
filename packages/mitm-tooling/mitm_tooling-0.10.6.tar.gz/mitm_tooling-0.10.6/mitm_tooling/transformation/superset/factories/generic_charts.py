import json
from uuid import UUID

from mitm_tooling.data_types import MITMDataType
from mitm_tooling.representation import ColumnName
from mitm_tooling.utilities.python_utils import unique

from ..definitions import (
    BigNumberAggregation,
    BigNumberChartParams,
    BigNumberTotalChartParams,
    DatasetIdentifier,
    HorizonChartParams,
    PieChartParams,
    QueryObjectExtras,
    QueryObjectFilterClause,
    SupersetAdhocFilter,
    SupersetAdhocMetric,
    SupersetAggregate,
    SupersetChartDef,
    SupersetVizType,
    TableChartParams,
    TimeGrain,
    TimeSeriesBarParams,
    TimeSeriesLineParams,
)
from .chart import mk_chart_def
from .core import (
    mk_adhoc_column,
    mk_adhoc_metric,
    mk_empty_adhoc_time_filter,
    mk_pivot_post_processing,
    mk_time_avg_post_processing,
)
from .query import mk_empty_query_object_time_filter_clause, mk_query_context, mk_query_object


def mk_pie_chart(
    name: str,
    dataset_identifier: DatasetIdentifier,
    col: ColumnName,
    dt: MITMDataType,
    groupby_cols: list[ColumnName] | None = None,
    uuid: UUID | None = None,
) -> SupersetChartDef:
    groupby_cols = groupby_cols or []
    metric = mk_adhoc_metric(col, agg=SupersetAggregate.COUNT, dt=dt)
    params = PieChartParams(
        datasource=dataset_identifier, metric=metric, groupby=groupby_cols, adhoc_filters=[mk_empty_adhoc_time_filter()]
    )
    # TODO may not be necessary to add groupby
    qo = mk_query_object(
        unique([col], groupby_cols), metrics=[metric], filters=[mk_empty_query_object_time_filter_clause()]
    )
    qc = mk_query_context(datasource=dataset_identifier, queries=[qo], form_data=params)

    return mk_chart_def(
        name=name,
        viz_type=SupersetVizType.PIE,
        dataset_uuid=dataset_identifier.uuid,
        params=params,
        query_context=qc,
        uuid=uuid,
    )


def mk_time_series_bar_chart(
    name: str,
    dataset_identifier: DatasetIdentifier,
    y_col: ColumnName,
    y_dt: MITMDataType,
    x_col: ColumnName,
    groupby_cols: list[ColumnName] | None = None,
    filters: list[SupersetAdhocFilter] | None = None,
    time_grain: TimeGrain | None = None,
    uuid: UUID | None = None,
) -> SupersetChartDef:
    groupby_cols = groupby_cols or []
    metric = mk_adhoc_metric(y_col, agg=SupersetAggregate.COUNT, dt=y_dt)
    adhoc_filters = [mk_empty_adhoc_time_filter()]
    if filters:
        adhoc_filters.extend(filters)
    params = TimeSeriesBarParams(
        datasource=dataset_identifier,
        metrics=[metric],
        groupby=groupby_cols,
        adhoc_filters=adhoc_filters,
        x_axis=x_col,
        time_grain_sqla=time_grain,
    )

    pp = mk_pivot_post_processing(
        x_col, cols=[y_col], aggregations={metric.label: 'mean'}, renames={metric.label: None}
    )
    adhoc_x = mk_adhoc_column(x_col, timeGrain=time_grain)
    qo = mk_query_object(
        columns=unique([adhoc_x, y_col], groupby_cols),
        metrics=[metric],
        filters=[QueryObjectFilterClause.from_adhoc_filter(af) for af in adhoc_filters],
        post_processing=pp,
        series_columns=[y_col],
    )
    qc = mk_query_context(datasource=dataset_identifier, queries=[qo], form_data=params)

    return mk_chart_def(
        name=name,
        viz_type=SupersetVizType.TIMESERIES_BAR,
        dataset_uuid=dataset_identifier.uuid,
        params=params,
        query_context=qc,
        uuid=uuid,
    )


def mk_avg_count_time_series_chart(
    name: str,
    dataset_identifier: DatasetIdentifier,
    groupby_cols: list[ColumnName] | None = None,
    time_col: ColumnName = 'time',
    filters: list[SupersetAdhocFilter] | None = None,
    time_grain: TimeGrain | None = None,
    uuid: UUID | None = None,
):
    groupby_cols = groupby_cols or []
    metric = mk_adhoc_metric(time_col, agg=SupersetAggregate.COUNT, dt=MITMDataType.Datetime)
    adhoc_filters = [mk_empty_adhoc_time_filter(col=time_col)]
    if filters:
        adhoc_filters.extend(filters)
    params = TimeSeriesLineParams(
        datasource=dataset_identifier,
        metrics=[metric],
        groupby=groupby_cols,
        adhoc_filters=adhoc_filters,
        x_axis=time_col,
        time_grain_sqla=time_grain,
    )

    pp = mk_pivot_post_processing(
        time_col, cols=groupby_cols, aggregations={metric.label: 'mean'}, renames={metric.label: None}
    )
    adhoc_time_col = mk_adhoc_column(time_col, timeGrain=time_grain)
    qo = mk_query_object(
        columns=unique([adhoc_time_col], groupby_cols),
        metrics=[metric],
        filters=[QueryObjectFilterClause.from_adhoc_filter(af) for af in adhoc_filters],
        post_processing=pp,
        series_columns=groupby_cols,
        extras=QueryObjectExtras(time_grain_sqla=time_grain),
    )
    qc = mk_query_context(datasource=dataset_identifier, queries=[qo], form_data=params)

    return mk_chart_def(
        name=name,
        viz_type=SupersetVizType.TIMESERIES_LINE,
        dataset_uuid=dataset_identifier.uuid,
        params=params,
        query_context=qc,
        uuid=uuid,
    )


def mk_metric_time_series_chart(
    name: str,
    metrics: list[SupersetAdhocMetric],
    dataset_identifier: DatasetIdentifier,
    groupby_cols: list[ColumnName] | None = None,
    time_col: ColumnName = 'time',
    filters: list[SupersetAdhocFilter] | None = None,
    time_grain: TimeGrain | None = None,
    uuid: UUID | None = None,
):
    groupby_cols = groupby_cols or []
    adhoc_filters = [mk_empty_adhoc_time_filter(col=time_col)]
    if filters:
        adhoc_filters.extend(filters)
    params = TimeSeriesLineParams(
        datasource=dataset_identifier,
        metrics=metrics,
        groupby=groupby_cols,
        adhoc_filters=adhoc_filters,
        x_axis=time_col,
        time_grain_sqla=time_grain,
    )
    # TODO decide whether to keep this, or fix if necessary
    pp = mk_time_avg_post_processing(groupby_cols, [m.label for m in metrics])

    adhoc_time_col = mk_adhoc_column(time_col, timeGrain=time_grain)
    qo = mk_query_object(
        columns=unique([adhoc_time_col], groupby_cols),
        metrics=metrics,
        filters=[QueryObjectFilterClause.from_adhoc_filter(af) for af in adhoc_filters],
        post_processing=pp,
        series_columns=groupby_cols,
        extras=QueryObjectExtras(time_grain_sqla=time_grain),
    )
    qc = mk_query_context(datasource=dataset_identifier, queries=[qo], form_data=params)

    return mk_chart_def(
        name=name,
        viz_type=SupersetVizType.TIMESERIES_LINE,
        dataset_uuid=dataset_identifier.uuid,
        params=params,
        query_context=qc,
        uuid=uuid,
    )


def mk_big_number_chart(
    name: str,
    metric: str | SupersetAdhocMetric,
    dataset_identifier: DatasetIdentifier,
    time_col: ColumnName | None = 'time',
    agg: BigNumberAggregation | None = 'sum',
    filters: list[SupersetAdhocFilter] | None = None,
    time_grain: TimeGrain | None = None,
    uuid: UUID | None = None,
):
    adhoc_filters = [mk_empty_adhoc_time_filter(col=time_col)]
    if filters:
        adhoc_filters.extend(filters)
    with_line = time_col and agg
    if with_line:
        params = BigNumberChartParams(
            datasource=dataset_identifier,
            metric=metric,
            x_axis=time_col,
            aggregation=agg,
            time_grain_sqla=time_grain,
            adhoc_filters=adhoc_filters,
        )
    else:
        params = BigNumberTotalChartParams(datasource=dataset_identifier, metric=metric)
    adhoc_time_col = mk_adhoc_column(time_col, timeGrain=time_grain)
    qo = mk_query_object(
        columns=[adhoc_time_col],
        metrics=[metric],
        filters=[QueryObjectFilterClause.from_adhoc_filter(af) for af in adhoc_filters],
        extras=QueryObjectExtras(time_grain_sqla=time_grain),
    )
    qc = mk_query_context(datasource=dataset_identifier, queries=[qo], form_data=params)

    return mk_chart_def(
        name=name,
        viz_type=SupersetVizType.BIG_NUMBER if with_line else SupersetVizType.BIG_NUMBER_TOTAL,
        dataset_uuid=dataset_identifier.uuid,
        params=params,
        query_context=qc,
        uuid=uuid,
    )


def mk_horizon_chart(
    name: str,
    metrics: list[str | SupersetAdhocMetric],
    dataset_identifier: DatasetIdentifier,
    groupby_cols: list[ColumnName],
    time_col: ColumnName = 'time',
    filters: list[SupersetAdhocFilter] | None = None,
    uuid: UUID | None = None,
):
    params = HorizonChartParams(
        datasource=dataset_identifier, metrics=metrics, groupby=groupby_cols, granularity_sqla=time_col
    )

    qo = mk_query_object(columns=groupby_cols, metrics=metrics, filters=filters)
    qc = mk_query_context(datasource=dataset_identifier, queries=[qo], form_data=params)

    return mk_chart_def(
        name=name,
        viz_type=SupersetVizType.HORIZON,
        dataset_uuid=dataset_identifier.uuid,
        params=params,
        query_context=qc,
        uuid=uuid,
    )


def mk_raw_table_chart(
    name: str,
    dataset_identifier: DatasetIdentifier,
    columns: list[ColumnName],
    filters: list[SupersetAdhocFilter] | None = None,
    orderby: list[tuple[ColumnName, bool]] | None = None,
    uuid: UUID | None = None,
) -> SupersetChartDef:
    adhoc_filters = filters or []
    params = TableChartParams(
        datasource=dataset_identifier,
        query_mode='raw',
        all_columns=columns,
        order_by_cols=[json.dumps(o) for o in orderby] if orderby else [],
        adhoc_filters=adhoc_filters,
        time_grain_sqla=TimeGrain.DAY,
    )

    qo = mk_query_object(
        columns=columns,
        filters=[QueryObjectFilterClause.from_adhoc_filter(af) for af in adhoc_filters],
        orderby=orderby,
        extras=QueryObjectExtras(time_grain_sqla=TimeGrain.DAY),
    )

    qc = mk_query_context(datasource=dataset_identifier, queries=[qo], form_data=params)

    return mk_chart_def(
        name=name,
        viz_type=SupersetVizType.TABLE,
        dataset_uuid=dataset_identifier.uuid,
        params=params,
        query_context=qc,
        uuid=uuid,
    )


def mk_agg_table_chart(
    name: str,
    dataset_identifier: DatasetIdentifier,
    metrics: list[str | SupersetAdhocMetric],
    groupby: list[ColumnName],
    filters: list[SupersetAdhocFilter] | None = None,
    orderby: list[str | SupersetAdhocMetric] | None = None,
    uuid: UUID | None = None,
):
    adhoc_filters = filters or []
    all_columns = []
    for m in metrics:
        if isinstance(m, str):
            all_columns.append(m)
        elif isinstance(m, SupersetAdhocMetric):
            all_columns.append(m.column.column_name)

    params = TableChartParams(
        datasource=dataset_identifier,
        query_mode='aggregate',
        all_columns=all_columns,
        order_by_cols=[json.dumps(o) for o in orderby] if orderby else [],
        metrics=metrics,
        groupby=groupby,
        adhoc_filters=adhoc_filters,
    )

    qo = mk_query_object(
        columns=groupby,
        metrics=metrics,
        filters=[QueryObjectFilterClause.from_adhoc_filter(af) for af in adhoc_filters],
        orderby=orderby,
    )

    qc = mk_query_context(datasource=dataset_identifier, queries=[qo], form_data=params)

    return mk_chart_def(
        name=name,
        viz_type=SupersetVizType.TABLE,
        dataset_uuid=dataset_identifier.uuid,
        params=params,
        query_context=qc,
        uuid=uuid,
    )
