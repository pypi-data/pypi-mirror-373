from typing import overload

import sqlalchemy as sa

from mitm_tooling.data_types import MITMDataType
from mitm_tooling.representation import ColumnName

from ..definitions import (
    FilterOperator,
    FilterStringOperators,
    Flatten,
    IdentifiedSupersetColumn,
    Pivot,
    PivotOperator,
    PivotOptions,
    Rename,
    RenameOptions,
    SupersetAdhocColumn,
    SupersetAdhocFilter,
    SupersetAdhocMetric,
    SupersetAggregate,
    SupersetColumn,
    SupersetId,
    SupersetMetric,
    SupersetPostProcessing,
)


def mk_pivot_post_processing(
    index_col: ColumnName,
    cols: list[ColumnName],
    aggregations: dict[ColumnName, str],
    renames: dict[ColumnName, ColumnName | None] | None = None,
) -> list[SupersetPostProcessing]:
    pp: list[SupersetPostProcessing] = [
        Pivot(
            options=PivotOptions(
                aggregates=[{c: PivotOperator(operator=m)} for c, m in aggregations.items()],
                columns=cols,
                index=[index_col],
            )
        )
    ]
    if renames:
        pp.append(Rename(options=RenameOptions(columns={c: rn for c, rn in renames.items()})))
    pp.append(Flatten())
    return pp


def mk_count_pivot_post_processing(
    cols: list[ColumnName], agg_cols: list[ColumnName], time_col: str = 'time'
) -> list[SupersetPostProcessing]:
    return mk_pivot_post_processing(time_col, cols, aggregations={f'AVG({c})': 'mean' for c in agg_cols})


def mk_time_avg_post_processing(
    cols: list[ColumnName], agg_cols: list[ColumnName], time_col: str = 'time'
) -> list[SupersetPostProcessing]:
    return mk_pivot_post_processing(time_col, cols, aggregations={f'AVG({c})': 'mean' for c in agg_cols})


def mk_adhoc_metric(
    col: ColumnName,
    agg: SupersetAggregate = SupersetAggregate.AVG,
    dt: MITMDataType = MITMDataType.Numeric,
    col_id: int | None = None,
    **kwargs,
) -> SupersetAdhocMetric:
    return SupersetAdhocMetric(label=f'{agg}({col})', aggregate=agg, column=mk_column(col, dt, col_id), **kwargs)


def mk_adhoc_metrics(
    cols: list[ColumnName],
    agg: SupersetAggregate = SupersetAggregate.AVG,
    dt: MITMDataType = MITMDataType.Numeric,
    **kwargs,
) -> list[SupersetAdhocMetric]:
    return [mk_adhoc_metric(c, agg=agg, dt=dt, **kwargs) for c in cols]


def mk_metric(col: ColumnName, agg: SupersetAggregate, **kwargs) -> SupersetMetric:
    name = f'{agg}({col})'
    return SupersetMetric(metric_name=name, verbose_name=name, expression=name, **kwargs)


def mk_metrics(
    cols: list[ColumnName], agg: SupersetAggregate = SupersetAggregate.AVG, **kwargs
) -> list[SupersetMetric]:
    return [mk_metric(c, agg, **kwargs) for c in cols]


@overload
def mk_column(col: ColumnName, dt: MITMDataType, dialect: sa.Dialect | None = None, **kwargs) -> SupersetColumn:
    pass


@overload
def mk_column(
    col: ColumnName, dt: MITMDataType, col_id: SupersetId, dialect: sa.Dialect | None = None, **kwargs
) -> IdentifiedSupersetColumn:
    pass


def mk_column(
    col: ColumnName, dt: MITMDataType, col_id: SupersetId | None = None, dialect: sa.Dialect | None = None, **kwargs
) -> SupersetColumn:
    args = (
        dict(
            column_name=col,
            is_dttm=dt is MITMDataType.Datetime,
            groupby=dt not in {MITMDataType.Json, MITMDataType.Numeric},
            type=(dt.sa_sql_type or MITMDataType.Text.sa_sql_type).compile(dialect=dialect),
        )
        | kwargs
    )
    if col_id is not None:
        return IdentifiedSupersetColumn(**args, id=col_id)
    else:
        return SupersetColumn(**args)


def mk_adhoc_column(col: ColumnName, **kwargs) -> SupersetAdhocColumn:
    return SupersetAdhocColumn(label=col, sqlExpression=col, **kwargs)


def mk_adhoc_filter(
    col: ColumnName, op: FilterOperator, comp: str | None = 'No Filter', **kwargs
) -> SupersetAdhocFilter:
    return SupersetAdhocFilter(
        subject=col, operator=op, operatorId=FilterStringOperators.from_operator(op), comparator=comp, **kwargs
    )


def mk_empty_adhoc_time_filter(col: ColumnName = 'time') -> SupersetAdhocFilter:
    return mk_adhoc_filter(col, FilterOperator.TEMPORAL_RANGE)
