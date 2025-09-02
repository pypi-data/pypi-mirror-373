import enum
import json
import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import datetime
from typing import Annotated, Any, Literal

import pandas as pd
import pydantic
import sqlalchemy as sa
from pydantic import Field
from sqlalchemy.sql import operators, sqltypes

from mitm_tooling.data_types import MITMDataType, SQL_DataType, WrappedMITMDataType, get_pandas_cast, get_sa_sql_type
from mitm_tooling.representation import ColumnName
from mitm_tooling.representation.sql.common import TableName
from mitm_tooling.utilities.python_utils import ExtraInfoExc

from ..data_models import AnyTableIdentifier, DBMetaInfo, SourceDBType, TableIdentifier, TypedRawQuery
from .df_transformation import PandasCreation, PandasDataframeTransform, PandasSeriesTransform, extract_json_path

logger = logging.getLogger(__name__)


class TableNotFoundException(ExtraInfoExc): ...


class ColumnNotFoundException(ExtraInfoExc): ...


class TransformationError(ExtraInfoExc): ...


class InvalidQueryException(ExtraInfoExc): ...


def map_sa_cols(
    from_clause: sa.FromClause,
    maps: dict[ColumnName, Callable[[sa.ColumnElement], sa.ColumnElement | None]],
    predicate: Callable[[sa.ColumnElement], bool] = None,
    keep_unmapped: bool = True,
) -> list[sa.ColumnElement]:
    res = []
    for n, c in from_clause.columns.items():
        if not predicate or predicate(c):
            if (keep_unmapped and (r := c) is not None) or (n in maps and (r := maps[n](c)) is not None):
                res.append(r)
    return res


def col_by_name(from_clause: sa.FromClause, name: ColumnName, raise_on_missing=False) -> sa.ColumnElement | None:
    res = next(iter(c for c in from_clause.columns if c.name == name), None)
    if res is None and raise_on_missing:
        raise ColumnNotFoundException(f'column {name} is not in {from_clause}')
    return res


def col_by_key(from_clause: sa.FromClause, key: ColumnName) -> sa.ColumnClause | None:
    return from_clause.columns.get(key, None)


class TransformOperation(pydantic.BaseModel, ABC):
    operation: str


class ColumnTransform(TransformOperation, PandasSeriesTransform, ABC):
    @abstractmethod
    def transform_column_element(self, col_element: sa.ColumnElement) -> sa.ColumnElement:
        pass


class ColumnCreation(TransformOperation, PandasCreation, ABC):
    @abstractmethod
    def make_column_elements(self, from_clause: sa.FromClause, **kwargs) -> list[sa.ColumnElement]:
        pass


class TableCreation(TransformOperation, ABC):
    @abstractmethod
    def make_from_clause(self, db_metas: dict[SourceDBType, DBMetaInfo], **kwargs) -> sa.FromClause:
        pass


class TableTransform(TransformOperation, PandasDataframeTransform, ABC):
    @abstractmethod
    def transform_from_clause(self, from_clause: sa.FromClause, **kwargs) -> sa.FromClause:
        pass


class SimpleSQLOperator(enum.StrEnum):
    ilike = 'ilike'
    like = 'like'
    eq = 'eq'
    ge = 'ge'
    gt = 'gt'
    le = 'le'
    lt = 'lt'
    in_op = 'in'
    not_in_op = 'notin'

    @property
    def sql_op(self) -> operators.OperatorType:
        match self:
            case SimpleSQLOperator.ilike:
                return operators.ilike_op
            case SimpleSQLOperator.like:
                return operators.like_op
            case SimpleSQLOperator.eq:
                return operators.eq
            case SimpleSQLOperator.ge:
                return operators.ge
            case SimpleSQLOperator.gt:
                return operators.gt
            case SimpleSQLOperator.le:
                return operators.le
            case SimpleSQLOperator.lt:
                return operators.lt
            case SimpleSQLOperator.in_op:
                return operators.in_op
            case SimpleSQLOperator.not_in_op:
                return operators.not_in_op

    def on_pandas(self, left: pd.Series, right: pd.Series) -> pd.Series:
        match self:
            case SimpleSQLOperator.ilike:
                return right.str.lower().find(left.str.lower())  # this is probably incorrect
            case SimpleSQLOperator.like:
                return right.str.find(left)
            case SimpleSQLOperator.eq:
                return left.eq(right)
            case SimpleSQLOperator.ge:
                return left.ge(right)
            case SimpleSQLOperator.gt:
                return left.gt(right)
            case SimpleSQLOperator.le:
                return left.le(right)
            case SimpleSQLOperator.lt:
                return left.lt(right)
            case SimpleSQLOperator.in_op:
                return left.map(lambda v: v in right)
            case SimpleSQLOperator.not_in_op:
                return left.map(lambda v: v not in right)


class SimpleWhere(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    lhs: ColumnName
    operator: SimpleSQLOperator
    rhs: ColumnName | tuple[Any, SQL_DataType]

    @pydantic.computed_field(repr=False)
    @property
    def rhs_is_literal(self) -> bool:
        return isinstance(self.rhs, tuple)

    def to_sa_operator(self, from_clause: sa.FromClause) -> operators.Operators:
        if self.rhs_is_literal:
            v, sql_dt = self.rhs
            sa_sql_dt = get_sa_sql_type(sql_dt)
            # TODO consider improving the 'literal rendering' logic here
            if (isinstance(sql_dt, WrappedMITMDataType) and sql_dt.mitm == MITMDataType.Datetime) or isinstance(
                sa_sql_dt, sqltypes.DATETIME
            ):
                v = datetime.fromisoformat(v)
            # if self.operator is SimpleSQLOperator.in_op or self.operator is SimpleSQLOperator.not_in_op:
            #    v = v.split(',')
            rhs = sa.literal(v, sa_sql_dt)
        else:
            rhs = col_by_name(from_clause, self.rhs)
        return self.operator.sql_op(col_by_name(from_clause, self.lhs), rhs)

    def to_df_mask(self, df: pd.DataFrame) -> pd.Series:
        if self.rhs_is_literal:
            v, sql_dt = self.rhs
            rhs = pd.Series(data=[v] * len(df), index=df.index)
            if (cast := get_pandas_cast(sql_dt)) is not None:
                rhs = cast(rhs)
        else:
            rhs = df[self.rhs]
        return self.operator.on_pandas(df[self.lhs], rhs)


class Limit(TableTransform):
    operation: Literal['limit'] = 'limit'
    limit: int

    def transform_from_clause(self, from_clause: sa.FromClause, **kwargs) -> sa.FromClause:
        return from_clause.select().limit(self.limit).subquery()

    def transform_df(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.iloc[: self.limit]


class TableFilter(TableTransform):
    operation: Literal['table_filter'] = 'table_filter'

    wheres: list[SimpleWhere]
    limit: int | None = None

    def transform_from_clause(self, from_clause: sa.FromClause, **kwargs) -> sa.FromClause:
        clause = from_clause.select().where(*(w.to_sa_operator(from_clause) for w in self.wheres))
        if self.limit is not None:
            clause = clause.limit(self.limit)
        return clause.subquery()

    def transform_df(self, df: pd.DataFrame) -> pd.DataFrame:
        mask = df.index != pd.NA  # should always be true # np.ones_like(df.index, dtype=bool)
        for m in [w.to_df_mask(df) for w in self.wheres]:
            mask &= m
        whered = df.loc[mask]
        return whered.iloc[: self.limit] if self.limit is not None else whered


class AddColumn(ColumnCreation):
    operation: Literal['add_column'] = 'add_column'

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    col_name: ColumnName
    value: Any
    target_type: SQL_DataType

    def make_column_elements(self, *args, **kwargs) -> list[sa.ColumnElement]:
        return [sa.literal_column(self.value, get_sa_sql_type(self.target_type)).label(self.col_name)]

    def make_series(self, df: pd.DataFrame) -> list[pd.Series]:
        cast = get_pandas_cast(self.target_type)
        s = pd.Series(name=self.col_name, data=[self.value] * len(df))
        return [cast(s) if cast is not None else s]

    # def transform_from_clause(self, sa_clause: sa.FromClause) -> sa.FromClause | tuple[
    #    sa.FromClause, TableMetaInfo]:
    #    cols = list(sa_clause.columns.values())
    #    i = min(self.index, len(cols))
    #    cols.insert(i, self.make_column_elements())
    #    return sa.select(*cols).subquery()


class CastColumn(ColumnTransform):
    operation: Literal['cast_column'] = 'cast_column'

    target_type: SQL_DataType

    def transform_column_element(self, col_element: sa.ColumnElement) -> sa.ColumnElement:
        return sa.cast(col_element, get_sa_sql_type(self.target_type))

    def transform_series(self, s: pd.Series) -> pd.Series:
        cast = get_pandas_cast(self.target_type)
        return cast(s) if cast is not None else s


class EditColumns(TableTransform):
    operation: Literal['edit_columns'] = 'edit_columns'

    transforms: dict[ColumnName, 'ColumnTransforms'] = Field(default_factory=dict)
    renames: dict[ColumnName, ColumnName] = Field(default_factory=dict)
    drops: set[ColumnName] = Field(default_factory=set)
    additions: dict[int, list['ColumnCreations']] = Field(default_factory=dict)

    def transform_from_clause(self, from_clause: sa.FromClause, **kwargs) -> sa.FromClause:
        selection = []
        for i, (_n, c) in enumerate(from_clause.columns.items()):
            col_name = c.name
            if i_additions := self.additions.get(i, None):
                for a in i_additions:
                    elements = a.make_column_elements(from_clause)
                    if elements:
                        selection.extend(elements)
            if col_transform := self.transforms.get(col_name, None):
                c = col_transform.transform_column_element(c)
            if new_name := self.renames.get(col_name, None):
                c = c.label(new_name)

            if col_name not in self.drops:
                selection.append(c)

        return sa.select(*selection).select_from(from_clause).subquery()

    def transform_df(self, df: pd.DataFrame) -> pd.DataFrame:
        selection = []
        for i, c in enumerate(df.columns):
            s = df[c]
            if i_additions := [a for j, a in self.additions if i == j]:
                for a in i_additions:
                    elements = a.make_series(df)
                    if elements:
                        selection.extend(elements)
            if col_transform := self.transforms.get(c, None):
                col_transform: ColumnTransform
                s = col_transform.transform_series(s)
            if new_name := self.renames.get(c, None):
                s.name = new_name
            if c not in self.drops:
                selection.append(s)

        dic = {s.name: s for s in selection}
        return pd.DataFrame(data=dic)


class ReselectColumns(TableTransform):
    operation: Literal['reselect_columns'] = 'reselect_columns'

    selection: list[ColumnName]

    def transform_from_clause(self, from_clause: sa.FromClause, **kwargs) -> sa.FromClause:
        if len(self.selection) > 0:
            return (
                sa.select(*(col_by_name(from_clause, n, raise_on_missing=True) for n in self.selection))
                .select_from(from_clause)
                .subquery()
            )
        else:
            return from_clause

    def transform_df(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.loc[:, list(self.selection)]


class ExtractJson(ColumnCreation):
    operation: Literal['extract_json'] = 'extract_json'

    json_col: ColumnName
    attributes: dict[ColumnName, tuple[str, ...]]

    def make_column_elements(self, from_clause: sa.FromClause, **kwargs) -> list[sa.ColumnElement]:
        # custom_op = operators.custom_op('->>', precedence=15, return_type=sqltypes.Text)

        c = col_by_name(from_clause, self.json_col)
        if c is None:
            logger.error(f'Column to extract json paths from does not exist: {self.json_col}')
            raise ColumnNotFoundException(f'Column to extract json paths from does not exist: {self.json_col}')
        else:
            # TODO srsly fix JSON extraction
            # print('\'' + '$.' + '.'.join(p) + '\'')

            # sa.literal('$.' + '.'.join(p), literal_execute=True)
            items_ = [
                sa.type_coerce(c, sqltypes.JSON(none_as_null=True))
                .op('->')(sa.literal(p, sa.JSON.JSONPathType))
                .label(a)
                for a, p in self.attributes.items()
            ]
            return items_

    def make_series(self, df: pd.DataFrame) -> list[pd.Series]:
        json_col = df[self.json_col].astype('str').map(json.loads)
        res = []
        for c, p in self.attributes.items():

            def map_func(v, p=p):
                return extract_json_path(v, p)

            extracted = json_col.map(map_func)
            res.append(pd.Series(name=c, data=extracted))
        return res


class ExistingTable(TableCreation):
    operation: Literal['existing'] = 'existing'

    base_table: AnyTableIdentifier

    def make_from_clause(self, db_metas: dict[SourceDBType, DBMetaInfo], **kwargs) -> sa.FromClause:
        if tm := TableIdentifier.resolve_id(self.base_table, db_metas):
            return tm.queryable_source
        else:
            raise TableNotFoundException(f'Base table does not exist: {self.base_table}')


class RawCompiled(TableCreation):
    operation: Literal['compiled'] = 'compiled'

    typed_query: TypedRawQuery

    def make_from_clause(self, db_metas: dict[SourceDBType, DBMetaInfo], **kwargs) -> sa.FromClause:
        return self.typed_query.to_from_clause()


class SimpleJoin(TableCreation):
    operation: Literal['join'] = 'join'

    left_table: AnyTableIdentifier
    right_table: AnyTableIdentifier
    on_cols_left: list[ColumnName] | None = None
    on_cols_right: list[ColumnName] | None = None
    is_outer: bool = False
    full: bool = False
    selected_cols_left: list[ColumnName] | None = None
    selected_cols_right: list[ColumnName] | None = None
    left_alias: TableName | None = None
    right_alias: TableName | None = None

    def make_from_clause(self, db_metas: dict[SourceDBType, DBMetaInfo], **kwargs) -> sa.FromClause:
        left_tm = TableIdentifier.resolve_id(self.left_table, db_metas)
        if left_tm is None:
            raise TableNotFoundException(f'Left base table for this join does not exist: {self.left_table}.')

        right_tm = TableIdentifier.resolve_id(self.right_table, db_metas)
        if right_tm is None:
            raise TableNotFoundException(f'Left base table for this join does not exist: {self.right_table}.')

        return self.make(left_tm.queryable_source, right_tm.queryable_source)

    def make(self, left_clause: sa.FromClause, right_clause: sa.FromClause) -> sa.FromClause:
        sa_left_clause = sa.alias(left_clause, self.left_alias) if self.left_alias else left_clause
        sa_right_clause = sa.alias(right_clause, self.right_alias) if self.right_alias else right_clause

        on_clause = None
        if self.on_cols_left and self.on_cols_right:
            on_clause = sa.and_(
                sa.true(),
                *(
                    lc == rc
                    for lc, rc in zip(
                        map(lambda n: col_by_name(sa_left_clause, n), self.on_cols_left),
                        map(lambda n: col_by_name(sa_right_clause, n), self.on_cols_right),
                        strict=False,
                    )
                    if lc is not None and rc is not None
                ),
            )

        join = sa.join(sa_left_clause, sa_right_clause, isouter=self.is_outer, full=self.full, onclause=on_clause)

        left_sel = (
            [col_by_name(sa_left_clause, n, raise_on_missing=True) for n in self.selected_cols_left]
            if self.selected_cols_left is not None
            else list(sa_left_clause.columns.values())
        )
        right_sel = (
            [col_by_name(sa_right_clause, n, raise_on_missing=True) for n in self.selected_cols_right]
            if self.selected_cols_right is not None
            else list(sa_right_clause.columns.values())
        )

        if self.left_alias:
            left_sel = [sa.label(f'{self.left_alias}.{c.name}', c) for c in left_sel]
        if self.right_alias:
            right_sel = [sa.label(f'{self.right_alias}.{c.name}', c) for c in right_sel]

        join = sa.select(*left_sel, *right_sel).select_from(join)

        return join.subquery()


ColumnCreations = Annotated[AddColumn | ExtractJson, Field(discriminator='operation')]
TableCreations = Annotated[SimpleJoin | ExistingTable | RawCompiled, Field(discriminator='operation')]
ColumnTransforms = Annotated[CastColumn, Field(discriminator='operation')]
TableTransforms = Annotated[EditColumns | ReselectColumns | TableFilter | Limit, Field(discriminator='operation')]

# ColumnCreations = Union[AddColumn, ExtractJson]
# TableCreations = Union[SimpleJoin, ExistingTable, RawCompiled]
# ColumnTransforms = Union[CastColumn]
# TableTransforms = Union[EditColumns, ReselectColumns, TableFilter, Limit]
