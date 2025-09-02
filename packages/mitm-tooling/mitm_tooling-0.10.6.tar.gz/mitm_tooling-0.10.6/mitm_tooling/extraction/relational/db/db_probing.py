import enum
import json
import logging
from collections.abc import Callable, Collection
from json import JSONDecodeError
from typing import Any

import genson
import pandas as pd
import sqlalchemy as sa
from sqlalchemy import Table
from sqlalchemy.sql import sqltypes

from mitm_tooling.data_types import MITMDataType
from mitm_tooling.representation import ColumnName
from mitm_tooling.utilities.sql_utils import AnyDBBind, use_db_bind

from ..data_models import DBMetaInfo, DBProbe, TableMetaInfo, TableProbe
from ..data_models.probe_models import (
    CategoricalSummaryStatistics,
    DatetimeSummaryStatistics,
    NumericSummaryStatistics,
    SampleSummary,
)

logger = logging.getLogger(__name__)


def initialize_db_probe(db_info: DBMetaInfo):
    return DBProbe(db_meta=db_info)


class SampleComputations(enum.StrEnum):
    Basic = 'basic'
    Unique = 'unique'
    ValueCounts = 'value_counts'
    NumericSummaryStatistics = 'numeric_summary_statistics'
    DatetimeSummaryStatistics = 'datetime_summary_statistics'
    CategoricalSummaryStatistics = 'categorical_summary_statistics'
    JSONSchema = 'json_schema'


def percentile_cl(s: str) -> str:
    return f'percentile_{s[:-1]}' if '%' in s else s


def clean_dict(arg: dict[str, Any], key_cleaner=lambda x: x, value_cleaner=lambda x: x) -> dict[str, Any]:
    return {key_cleaner(k): value_cleaner(v) for k, v in arg.items()}


summary_computers: dict[SampleComputations, tuple[Callable[[pd.Series], SampleSummary], set[str]]] = {
    SampleComputations.Basic: (
        lambda s: SampleSummary(sample_size=(L := len(s)), na_fraction=(L - s.count()) / L if L > 0 else 0.0),
        {'sample_size', 'na_fraction'},
    ),
    SampleComputations.Unique: (
        lambda s: SampleSummary(unique_fraction=(s.nunique() / L) if (L := len(s)) > 0 else 0.0),
        {'unique_fraction'},
    ),
    SampleComputations.ValueCounts: (
        lambda s: SampleSummary(value_counts=clean_dict(s.value_counts(normalize=False).to_dict(), lambda k: str(k))),
        {'value_counts'},
    ),
    SampleComputations.NumericSummaryStatistics: (
        lambda s: SampleSummary(
            summary_statistics=(
                NumericSummaryStatistics.model_validate(clean_dict(s.describe().to_dict(), percentile_cl))
            )
            if len(s) > 0
            else NumericSummaryStatistics.empty()
        ),
        {'summary_statistics'},
    ),
    SampleComputations.DatetimeSummaryStatistics: (
        lambda s: SampleSummary(
            summary_statistics=(
                DatetimeSummaryStatistics.model_validate(
                    clean_dict(
                        s.describe().to_dict(),
                        percentile_cl,
                        lambda v: (v.to_pydatetime(warn=False) if isinstance(v, pd.Timestamp) else v),
                    )
                )
            )
            if len(s) > 0
            else DatetimeSummaryStatistics.empty()
        ),
        {'summary_statistics'},
    ),
    SampleComputations.CategoricalSummaryStatistics: (
        lambda s: SampleSummary(
            summary_statistics=(
                CategoricalSummaryStatistics.model_validate(s.describe().to_dict())
                if len(s) > 0
                else CategoricalSummaryStatistics.empty()
            )
        ),
        {'summary_statistics'},
    ),
    SampleComputations.JSONSchema: (lambda s: SampleSummary(json_schema=build_schema(s)), {'json_schema'}),
}


def build_schema(s: pd.Series, return_series=False) -> dict | tuple[dict, pd.Series] | None:
    from pandas.core.dtypes.common import is_string_dtype

    if is_string_dtype(s):
        try:
            s = s.apply(json.loads)
        except JSONDecodeError:
            return
    try:
        schema_builder = genson.SchemaBuilder(schema_uri=False)
        for o in s:
            schema_builder.add_object(o)
        json_schema = schema_builder.to_schema()
        return (json_schema, s) if return_series else json_schema
    except genson.SchemaGenerationError:
        return None


def try_datetime(s: pd.Series) -> pd.Series | None:
    # FUTURE: support epoch seconds timestamps as well as datetime strings
    if s.isna().all():
        return None
    try:
        dt_col = pd.to_datetime(s, errors='raise', utc=True, format='ISO8601')
        return dt_col
    except ValueError:
        pass


def try_json(s: pd.Series) -> tuple[pd.Series, SampleSummary] | None:
    res = build_schema(s, return_series=True)
    if res is not None:
        json_schema, s = res
        return s, SampleSummary(json_schema=json_schema)  # {SampleComputations.JSONSchema.value: json_schema}
    return None


def guess_table_index_cols(table: Table) -> list[ColumnName] | None:
    index = next(iter(table.indexes), None)
    if index is not None:
        return list(index.columns)
    else:
        return list(table.primary_key)


def query_row_count(bind: AnyDBBind, from_clause: sa.FromClause) -> int:
    with use_db_bind(bind) as conn:
        return conn.scalar(sa.select(sa.sql.func.count()).select_from(from_clause))


def test_query(bind: AnyDBBind, from_clause: sa.FromClause) -> bool:
    with use_db_bind(bind) as conn:
        res = conn.execute(from_clause.select().limit(1)).all()
    logger.info(f'Tested new virtual view query: {from_clause}\nResult: {res}')
    return len(res) <= 1


def sample_queryable(
    bind: AnyDBBind, from_clauses: Collection[sa.FromClause], sample_size: int = 100, query_via_pandas=False
) -> list[tuple[sa.FromClause, pd.DataFrame]]:
    samples = []

    with use_db_bind(bind) as conn:
        for from_clause in from_clauses:
            selection = from_clause.select().limit(sample_size)
            if query_via_pandas:
                q = str(selection.compile(bind=conn))
                df = pd.read_sql_query(q, conn)  # , index_col=guess_table_index_cols(from_clause)
            else:
                df = pd.DataFrame.from_records(
                    conn.execute(selection).all(), columns=[c.name for c in from_clause.columns]
                )  # , index=guess_table_index_cols(from_clause)

            samples.append((from_clause, df))

    return samples


def infer_dtypes(
    from_clause: sa.FromClause, samples: pd.DataFrame | dict[str, pd.Series]
) -> tuple[dict[ColumnName, MITMDataType], dict[ColumnName, pd.Series], dict[ColumnName, SampleSummary]]:
    from pandas.api.types import (
        is_bool_dtype,
        is_datetime64_any_dtype,
        is_integer_dtype,
        is_numeric_dtype,
        is_string_dtype,
    )

    inferred_dts = {}
    conv_cols = {}
    sample_summaries = {}
    for c in samples.columns if isinstance(samples, pd.DataFrame) else samples:
        sql_col: sa.Column = from_clause.columns[c]
        col_sample = samples[c]
        conv_col = col_sample.convert_dtypes()
        conv_col_dt = conv_col.dtype

        inferred_dt = MITMDataType.Unknown
        if len(col_sample) > 0:
            if isinstance(sql_col.type, sqltypes.LargeBinary | sqltypes.BINARY):
                inferred_dt = MITMDataType.Unknown  # TODO reintroduce or remove
            else:
                for dt, cond in [
                    (MITMDataType.Boolean, is_bool_dtype),
                    (MITMDataType.Datetime, is_datetime64_any_dtype),
                    (MITMDataType.Integer, is_integer_dtype),
                    (MITMDataType.Numeric, is_numeric_dtype),
                    (MITMDataType.Text, is_string_dtype),
                ]:
                    if cond(conv_col_dt):
                        inferred_dt = dt
                        break
            if inferred_dt is MITMDataType.Text:
                for sub_dt, inferrer in [(MITMDataType.Datetime, try_datetime), (MITMDataType.Json, try_json)]:
                    if (inf_res := inferrer(col_sample)) is not None:
                        inferred_dt = sub_dt
                        if isinstance(inf_res, tuple) and len(inf_res) == 2:
                            conv_col, sample_summary = inf_res
                            sample_summaries[c] = sample_summary
                        else:
                            conv_col = inf_res
                        break

        inferred_dts[c] = inferred_dt
        conv_cols[c] = conv_col
    return inferred_dts, conv_cols, sample_summaries


def summarize_sample(
    sample: pd.Series,
    comps: set[SampleComputations],
    baseline_computers=(SampleComputations.Basic,),
    init_summary: SampleSummary | None = None,
) -> SampleSummary:
    res: dict[str, Any] = init_summary.model_dump(exclude_none=True, exclude_unset=True) if init_summary else {}
    for comp in set(baseline_computers) | comps:
        f, props = summary_computers[comp]
        if any(res.get(p, None) is None for p in props):
            res.update(f(sample).model_dump(exclude_none=True, exclude_unset=True))
    return SampleSummary(**res)


def summarize_samples(
    samples: dict[ColumnName, pd.Series] | pd.DataFrame,
    computations: dict[ColumnName, set[SampleComputations]],
    init_summaries: dict[ColumnName, SampleSummary] | None = None,
) -> dict[ColumnName, SampleSummary]:
    res = {}
    for c, comps in computations.items():
        s = samples[c]
        res[c] = summarize_sample(s, comps, init_summary=init_summaries.get(c, None) if init_summaries else None)
    return res


def analyze_queryable_sample(
    from_clause: sa.FromClause, table_sample: pd.DataFrame
) -> tuple[dict[ColumnName, MITMDataType], dict[ColumnName, SampleSummary]]:
    inferred_dts, conv_cols, sample_summaries = infer_dtypes(from_clause, table_sample)

    computations = {}
    for c, dt in inferred_dts.items():
        match dt:
            case MITMDataType.Integer:
                computations[c] = {SampleComputations.NumericSummaryStatistics, SampleComputations.Unique}
            case MITMDataType.Numeric:
                computations[c] = {SampleComputations.NumericSummaryStatistics}
            case MITMDataType.Boolean:
                computations[c] = {SampleComputations.ValueCounts}
            case MITMDataType.Json:
                computations[c] = {SampleComputations.JSONSchema}
            case MITMDataType.Datetime:
                computations[c] = {SampleComputations.DatetimeSummaryStatistics}
            case MITMDataType.Text:
                computations[c] = {SampleComputations.Unique, SampleComputations.CategoricalSummaryStatistics}
            case MITMDataType.Unknown | MITMDataType.Infer:
                computations[c] = {SampleComputations.Unique}

    sample_summaries = summarize_samples(conv_cols, computations, init_summaries=sample_summaries)

    return inferred_dts, sample_summaries


def create_table_probe(bind: AnyDBBind, table_meta: TableMetaInfo, sample_size: int = 100) -> TableProbe:
    queryable_source = table_meta.queryable_source
    with use_db_bind(bind) as conn:
        row_count = query_row_count(conn, queryable_source)
        _, df = sample_queryable(conn, {queryable_source}, sample_size=sample_size)[0]
    inferred_types, sample_summaries = analyze_queryable_sample(queryable_source, df)
    sampled_values = {str(c): [str(v) for v in vs] for c, vs in df.to_dict(orient='list').items()}
    return TableProbe(
        table_meta=table_meta,
        row_count=row_count,
        sampled_values=sampled_values,
        inferred_types=inferred_types,
        sample_summaries=sample_summaries,
    )


def create_db_probe(bind: AnyDBBind, db_meta: DBMetaInfo, sample_size: int = 100) -> DBProbe:
    db_probe = initialize_db_probe(db_meta)
    with use_db_bind(bind) as conn:
        table_probes = (
            (tm.short_table_identifier, create_table_probe(conn, tm, sample_size=sample_size))
            for tm in db_meta.tables.values()
        )
    db_probe.update_probes(*table_probes)
    return db_probe
