import logging
import re
from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Callable, Coroutine
from datetime import UTC, datetime
from typing import Annotated, Any, Self

import pydantic
import sqlalchemy as sa
from pydantic import BeforeValidator, Field, NonNegativeInt, PlainSerializer

from mitm_tooling.data_types import MITMDataType, SA_SQLTypeName

from ..data_models.db_meta import DBMetaInfo, ExplicitColumnSelection, ExplicitTableSelection, TableMetaInfo
from ..data_models.db_probe import DBProbe, TableProbe
from ..data_models.probe_models import DatetimeSummaryStatistics, FloatPercentage, NumericSummaryStatistics

logger = logging.getLogger(__name__)

CustomDatetime = Annotated[
    datetime,
    BeforeValidator(lambda x: datetime.fromisoformat(x).astimezone(tz=UTC)),
    PlainSerializer(lambda x: datetime.isoformat(x)),
]


class ColumnCondition(pydantic.BaseModel, ABC):
    @abstractmethod
    def test(self, c: sa.Column, table_meta: TableMetaInfo, **kwargs) -> bool:
        pass


class TableCondition(pydantic.BaseModel, ABC):
    @abstractmethod
    def test(self, t: sa.Table, table_meta: TableMetaInfo, **kwargs) -> bool:
        pass


class SyntacticColumnCondition(ColumnCondition):
    name_regex: str | None = None
    sql_data_type: SA_SQLTypeName | None = None
    mitm_data_type: MITMDataType | None = None

    def test(self, c: sa.Column, table_meta: TableMetaInfo, **kwargs) -> bool:
        name_condition = not self.name_regex or re.search(self.name_regex, c.name)
        sql_dt_condition = not self.sql_data_type or self.sql_data_type == str(c.type)
        mitm_dt_condition = (
            not self.mitm_data_type or self.mitm_data_type == table_meta.column_properties[c.name].mitm_data_type
        )
        return name_condition and sql_dt_condition and mitm_dt_condition


class SemanticColumnCondition(ColumnCondition):
    # sql_condition: str | None = None
    inferred_data_type: MITMDataType | None = None
    max_na_fraction: FloatPercentage | None = None
    value_in_range: Any | None = None
    contained_value: Any | None = None  # remember this is evaluated on just a sample!
    contained_datetime: CustomDatetime | None = None

    def test(self, c: sa.Column, table_meta: TableMetaInfo, table_probe: TableProbe = None, **kwargs) -> bool:
        if not table_probe:
            return False
        else:
            inferred_data_type_condition = (
                not self.inferred_data_type or self.inferred_data_type == table_probe.inferred_types[c.name]
            )
            na_condition = not self.max_na_fraction or (
                (na_fraction := table_probe.sample_summaries[c.name].na_fraction) is None
                or na_fraction <= self.max_na_fraction
            )
            range_condition = not self.value_in_range or (
                (summary_statistics := table_probe.sample_summaries[c.name].summary_statistics) is None
                or (
                    isinstance(summary_statistics, NumericSummaryStatistics)
                    and (summary_statistics.min <= self.value_in_range <= summary_statistics.max)
                )
            )
            datetime_condition = not self.contained_datetime or (
                (summary_statistics := table_probe.sample_summaries[c.name].summary_statistics) is None
                or (
                    isinstance(summary_statistics, DatetimeSummaryStatistics)
                    and (summary_statistics.min <= self.contained_datetime <= summary_statistics.max)
                )
            )
            return inferred_data_type_condition and na_condition and range_condition and datetime_condition


class SyntacticTableCondition(TableCondition):
    schema_regex: str | None = None
    name_regex: str | None = None
    min_col_count: NonNegativeInt | None = None
    max_col_count: NonNegativeInt | None = None
    has_foreign_key: bool | None = None

    def test(self, t: sa.Table, table_meta: TableMetaInfo, **kwargs) -> bool:
        regex_condition = (not self.schema_regex or re.search(self.schema_regex, t.schema)) and (
            not self.name_regex or re.search(self.name_regex, t.name)
        )
        fk_condition = not self.has_foreign_key or len(table_meta.foreign_key_constraints) > 0
        col_count_condition = (not self.min_col_count or self.min_col_count <= len(table_meta.columns)) and (
            not self.max_col_count or len(table_meta.columns) <= self.max_col_count
        )
        return regex_condition and fk_condition and col_count_condition


class SemanticTableCondition(TableCondition):
    min_row_count: NonNegativeInt | None = None
    max_row_count: NonNegativeInt | None = None

    def test(self, t: sa.Table, table_meta: TableMetaInfo, table_probe: TableProbe = None, **kwargs) -> bool:
        if not table_probe:
            return False
        else:
            count_condition = (not self.min_row_count or self.min_row_count <= table_probe.row_count) and (
                not self.max_row_count or table_probe.row_count <= self.max_row_count
            )
            return count_condition


class DBMetaQuery(pydantic.BaseModel):
    syntactic_table_conditions: list[SyntacticTableCondition] = Field(default_factory=list)
    semantic_table_conditions: list[SemanticTableCondition] = Field(default_factory=list)
    syntactic_column_conditions: list[SyntacticColumnCondition] = Field(default_factory=list)
    semantic_column_conditions: list[SemanticColumnCondition] = Field(default_factory=list)

    @classmethod
    def from_conditions(cls, *args) -> Self:
        syn_tc, sem_tc, syn_cc, sem_cc = [], [], [], []
        for a in args:
            if isinstance(a, SyntacticTableCondition):
                syn_tc.append(a)
            elif isinstance(a, SemanticTableCondition):
                sem_tc.append(a)
            elif isinstance(a, SyntacticColumnCondition):
                syn_cc.append(a)
            elif isinstance(a, SemanticColumnCondition):
                sem_cc.append(a)
        return cls(
            syntactic_table_conditions=syn_tc,
            semantic_table_conditions=sem_tc,
            syntactic_column_conditions=syn_cc,
            semantic_column_conditions=sem_cc,
        )

    @staticmethod
    def _filter(
        table_conditions: list[TableCondition],
        col_conditions: list[ColumnCondition],
        db_meta: DBMetaInfo,
        test_kwargler=lambda t, tm: {},
        pre_selection: ExplicitTableSelection | None = None,
        col_pre_selection: ExplicitColumnSelection | None = None,
        return_column_condition_witnesses: bool = True,
    ) -> ExplicitTableSelection | tuple[ExplicitTableSelection, ExplicitColumnSelection]:
        res = defaultdict(set)
        column_condition_witnesses = defaultdict(dict)
        tables_to_consider = (
            (
                tm
                for schema, tables in pre_selection.items()
                for table in tables
                if (tm := db_meta.search_table(schema, table))
            )
            if pre_selection is not None
            else db_meta.tables.values()
        )
        for table_meta in tables_to_consider:
            t = table_meta.sa_table
            syn_conditions = all(
                tc.test(t, table_meta=table_meta, **test_kwargler(t, table_meta)) for tc in table_conditions
            )
            if syn_conditions:
                cols_to_consider = [
                    t.columns[c]
                    for c in (
                        (col_pre_selection.get(table_meta.schema_name, {}).get(table_meta.name, set()))
                        if col_pre_selection is not None
                        else table_meta.columns
                    )
                ]
                syn_col_condition_witnesses = {
                    c.name
                    for c in cols_to_consider
                    if all(cc.test(c, table_meta=table_meta, **test_kwargler(t, table_meta)) for cc in col_conditions)
                }
                if syn_col_condition_witnesses:
                    res[table_meta.schema_name].add(table_meta.name)
                    column_condition_witnesses[table_meta.schema_name][table_meta.name] = syn_col_condition_witnesses
        res = ExplicitTableSelection(**res)
        return (res, column_condition_witnesses) if return_column_condition_witnesses else res

    def filter_syntactic(
        self,
        db_meta: DBMetaInfo,
        pre_selection: ExplicitTableSelection | None = None,
        col_pre_selection: ExplicitColumnSelection | None = None,
        return_column_condition_witnesses: bool = True,
    ) -> ExplicitTableSelection | tuple[ExplicitTableSelection, ExplicitColumnSelection]:
        return self._filter(
            self.syntactic_table_conditions,
            self.syntactic_column_conditions,
            db_meta,
            pre_selection=pre_selection,
            col_pre_selection=col_pre_selection,
            return_column_condition_witnesses=return_column_condition_witnesses,
        )

    def filter_semantic(
        self,
        db_meta: DBMetaInfo,
        db_probe: DBProbe,
        pre_selection: ExplicitTableSelection | None = None,
        col_pre_selection: ExplicitColumnSelection | None = None,
        return_column_condition_witnesses: bool = True,
    ) -> ExplicitTableSelection | tuple[ExplicitTableSelection, ExplicitColumnSelection]:
        def test_kwargler(t: sa.Table, tm: TableMetaInfo, db_probe: DBProbe = db_probe) -> dict:
            return dict(table_probe=db_probe.table_probes.get(tm.short_table_identifier, None))

        return self._filter(
            self.semantic_table_conditions,
            self.semantic_column_conditions,
            db_meta,
            test_kwargler=test_kwargler,
            pre_selection=pre_selection,
            col_pre_selection=col_pre_selection,
            return_column_condition_witnesses=return_column_condition_witnesses,
        )


async def resolve_db_meta_query(
    db_meta_query: DBMetaQuery,
    db_meta: DBMetaInfo,
    db_prober: Callable[[ExplicitTableSelection], Coroutine[Any, Any, DBProbe]],
    filter_columns=False,
    use_shallow_filter: bool = True,
) -> DBMetaInfo:
    logger.info(f'Received search query: {db_meta_query.model_dump(exclude_none=True)}')
    table_sub_selection, column_condition_witnesses = db_meta_query.filter_syntactic(
        db_meta, return_column_condition_witnesses=True
    )

    logger.info(f'Getting probes for pre-selected tables: {table_sub_selection}')
    db_probe = await db_prober(table_sub_selection)

    table_selection = None
    try:
        table_selection, column_condition_witnesses = db_meta_query.filter_semantic(
            db_meta,
            db_probe,
            pre_selection=table_sub_selection,
            col_pre_selection=(column_condition_witnesses if filter_columns else None),
            return_column_condition_witnesses=True,
        )
    except Exception as e:
        logger.error(f'Search resulted in error:\n{e}')
        raise e

    logger.info(f'Search resulted in: {table_selection}')

    fun = db_meta.filter_shallow if use_shallow_filter else db_meta.filter
    return fun(table_selection, column_selection=(column_condition_witnesses if filter_columns else None))


def resolve_db_meta_selection(
    selection: ExplicitTableSelection | ExplicitColumnSelection,
    db_meta: DBMetaInfo,
    filter_columns=False,
    use_shallow_filter: bool = True,
) -> DBMetaInfo:
    fun = db_meta.filter_shallow if use_shallow_filter else db_meta.filter
    if (v := next(iter(selection), None)) is not None:
        if isinstance(v, dict):
            table_selection = {schema: set(table_col_dict.keys()) for schema, table_col_dict in v.items()}
            return fun(table_selection, (selection if filter_columns else None))
    return fun(selection)
