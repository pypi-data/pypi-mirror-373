from mitm_tooling.representation import ColumnName

from ..definitions import (
    ChartDatasource,
    DatasetIdentifier,
    FilterOperator,
    FilterValues,
    FormData,
    QueryContext,
    QueryObject,
    QueryObjectFilterClause,
    SupersetAdhocColumn,
    SupersetAdhocMetric,
    SupersetPostProcessing,
)


def mk_query_object_filter_clause(
    col: ColumnName, op: FilterOperator, val: FilterValues | None = None, **kwargs
) -> QueryObjectFilterClause:
    return QueryObjectFilterClause(col=col, op=op, val=val, **kwargs)


def mk_empty_query_object_time_filter_clause() -> QueryObjectFilterClause:
    return mk_query_object_filter_clause('time', FilterOperator.TEMPORAL_RANGE)


def mk_query_object(
    columns: list[ColumnName | SupersetAdhocColumn] | None = None,
    metrics: list[str | SupersetAdhocMetric] | None = None,
    filters: list[QueryObjectFilterClause] | None = None,
    orderby: list[tuple[str | SupersetAdhocMetric, bool]] | None = None,
    post_processing: list[SupersetPostProcessing] | None = None,
    row_limit: int | None = 10_000,
    **kwargs,
) -> QueryObject:
    columns = columns or []
    metrics = metrics or []
    filters = filters or []
    if orderby is None and len(metrics) > 0:
        orderby = [(metrics[0], 0)]
    elif orderby is None:
        orderby = []
    if post_processing is None:
        post_processing = []
    return QueryObject(
        columns=columns,
        metrics=metrics,
        filters=filters,
        orderby=orderby,
        post_processing=post_processing,
        row_limit=row_limit,
        **kwargs,
    )


def mk_query_context(
    datasource: DatasetIdentifier, queries: list[QueryObject], form_data: FormData, **kwargs
) -> QueryContext:
    return QueryContext(
        datasource=ChartDatasource.from_identifier(datasource), queries=queries, form_data=form_data, **kwargs
    )
