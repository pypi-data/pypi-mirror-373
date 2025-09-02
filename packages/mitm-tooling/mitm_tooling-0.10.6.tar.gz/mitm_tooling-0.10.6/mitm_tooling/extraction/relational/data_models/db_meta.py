from __future__ import annotations

from collections.abc import Callable
from functools import cached_property
from typing import Self

import pydantic
import sqlalchemy as sa
from pydantic import Field
from sqlalchemy import MetaData, Table

from mitm_tooling.data_types import MITMDataType, SA_SQLTypeName, sa_sql_to_mitm_type
from mitm_tooling.representation.sql import ColumnName, Queryable, SchemaName, ShortTableIdentifier, TableName
from mitm_tooling.utilities.sql_utils import unqualify

from .table_identifiers import AnyLocalTableIdentifier, LocalTableIdentifier

ExplicitTableSelection = dict[SchemaName, set[TableName]]
ExplicitColumnSelection = dict[SchemaName, dict[TableName, set[ColumnName]]]


class ExplicitSelectionUtils:
    @classmethod
    def surviving_cols(
        cls,
        tm: TableMetaInfo | None,
        table_selection: ExplicitTableSelection | None,
        column_selection: ExplicitColumnSelection | None,
    ) -> list[ColumnName]:
        table_ok = cls.table_survives(tm, table_selection)
        return (
            [c for c in tm.columns if column_selection is None or c in cls.relevant_col_set(tm, column_selection)]
            if table_ok
            else []
        )

    @classmethod
    def table_survives(cls, tm: TableMetaInfo | None, table_selection: ExplicitTableSelection | None) -> bool:
        return tm is not None and (table_selection is None or tm.name in table_selection.get(tm.schema_name, {}))

    @classmethod
    def relevant_col_set(
        cls, tm: TableMetaInfo | None, column_selection: ExplicitColumnSelection | None
    ) -> set[ColumnName] | None:
        return (
            column_selection.get(tm.schema_name, {}).get(tm.name, None) if tm is not None and column_selection else None
        )


class ForeignKeyConstraintBase(pydantic.BaseModel):
    name: str | None = None
    table: AnyLocalTableIdentifier
    columns: list[ColumnName]
    target_table: AnyLocalTableIdentifier
    target_columns: list[ColumnName]

    def to_sa_constraint(self, db_meta: DBMetaInfo) -> sa.ForeignKeyConstraint | None:
        t = LocalTableIdentifier.resolve_id(self.table, db_meta)
        ref_t = LocalTableIdentifier.resolve_id(self.target_table, db_meta)
        if t is not None and ref_t is not None:
            return sa.ForeignKeyConstraint(
                columns=[t.sa_table.c[c] for c in self.columns],
                refcolumns=[ref_t.sa_table.c[c] for c in self.target_columns],
                name=self.name,
            )
        return None


class ForeignKeyConstraint(ForeignKeyConstraintBase):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    sa_table: sa.Table
    sa_target_table: sa.Table
    sa_constraint: sa.ForeignKeyConstraint

    @classmethod
    def from_sa_constraint(cls, fkc: sa.ForeignKeyConstraint, default_schema: SchemaName) -> Self:
        cols, target_cols = zip(
            *[(fk.column.name, unqualify(fk.target_fullname)[-1]) for fk in fkc.elements], strict=False
        )
        table_schema = fkc.table.schema if fkc.table.schema else default_schema
        target_schema = fkc.referred_table.schema if fkc.referred_table.schema else default_schema
        return ForeignKeyConstraint(
            name=fkc.name,
            table=(table_schema, fkc.table.name),
            columns=cols,
            target_table=(target_schema, fkc.referred_table.name),
            target_columns=target_cols,
            sa_constraint=fkc,
            sa_table=fkc.table,
            sa_target_table=fkc.referred_table,
        )

    def is_still_valid(
        self,
        dbm: DBMetaInfo,
        tm: TableMetaInfo,
        table_selection: ExplicitTableSelection | None = None,
        column_selection: ExplicitColumnSelection | None = None,
    ) -> bool:
        target_tm = LocalTableIdentifier.resolve_id(self.target_table, dbm)
        self_valid = set(self.columns) <= set(
            ExplicitSelectionUtils.surviving_cols(tm, table_selection, column_selection)
        )
        referred_valid = set(self.target_columns) <= set(
            ExplicitSelectionUtils.surviving_cols(target_tm, table_selection, column_selection)
        )
        return self_valid and referred_valid


class ColumnProperties(pydantic.BaseModel):
    nullable: bool
    unique: bool
    part_of_pk: bool
    part_of_fk: bool
    part_of_index: bool
    mitm_data_type: MITMDataType


class TableMetaInfoBase(pydantic.BaseModel):
    """
    This model represents the metadata of a table in a relational database.
    It is serializable and can be used for exchange.
    """

    schema_name: SchemaName = Field(default='main')
    name: TableName
    columns: list[ColumnName]
    sql_column_types: list[SA_SQLTypeName]
    primary_key: list[ColumnName] | None = None
    indexes: list[list[ColumnName]] | None = Field(default_factory=list)
    foreign_key_constraints: list[ForeignKeyConstraintBase] = Field(default_factory=list)
    column_properties: dict[ColumnName, ColumnProperties] = Field(default_factory=dict)

    @cached_property
    def col_set(self) -> set[ColumnName]:
        return set(self.columns)

    @cached_property
    def short_table_identifier(self) -> ShortTableIdentifier:
        return self.schema_name, self.name


class TableMetaInfo(TableMetaInfoBase):
    """
    This model represents the metadata of a table in a relational database.
    It extends the base model with additional information about the source of the table, in particular a SQLAlchemy `Table` object and a `Queryable`.
    It is therefore not serializable.
    """

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    foreign_key_constraints: list[ForeignKeyConstraint] = Field(default_factory=list)
    sa_table: Table
    queryable_source: Queryable

    @classmethod
    def from_sa_table(
        cls, t: Table, queryable_source: Queryable | None = None, default_schema: str | None = None
    ) -> Self:
        fkcs = [
            ForeignKeyConstraint.from_sa_constraint(fkc, t.schema or default_schema)
            for fkc in t.foreign_key_constraints
        ]
        col_props = {
            c.name: ColumnProperties(
                nullable=c.nullable,
                unique=bool(c.unique),
                part_of_index=any(c.name in ind.columns for ind in t.indexes),
                part_of_pk=c.primary_key,
                part_of_fk=len(c.foreign_keys) > 0,
                mitm_data_type=sa_sql_to_mitm_type(c.type),
            )
            for c in t.columns
        }
        return cls(
            name=t.name,
            columns=[c.name for c in t.columns],
            sql_column_types=[str(c.type) for c in t.columns],
            primary_key=[c.name for c in t.primary_key] if t.primary_key else None,
            indexes=[list(ind.columns.keys()) for ind in t.indexes],
            foreign_key_constraints=fkcs,
            schema_name=t.schema or default_schema,
            column_properties=col_props,
            sa_table=t,
            queryable_source=queryable_source if queryable_source is not None else t,
        )

    def filter_shallow(self, column_selection: set[ColumnName] | None = None) -> Self:
        if column_selection is None:
            return self.model_copy(deep=True)
        else:
            cols = [c for c in self.columns if c in column_selection]
            sql_column_types = [str(self.sa_table.columns[c].type) for c in cols]
            primary_key = self.primary_key if all(c in column_selection for c in self.primary_key) else None
            indexes = [ind for ind in self.indexes if all(c in column_selection for c in ind)]
            fkcs = [fkc for fkc in self.foreign_key_constraints if all(c in column_selection for c in fkc.columns)]
            col_props = {c: props for c, props in self.column_properties.items() if c in column_selection}
            return self.__class__(
                name=self.name,
                schema_name=self.schema_name,
                sa_table=self.sa_table,
                columns=cols,
                sql_column_types=sql_column_types,
                primary_key=primary_key,
                indexes=indexes,
                foreign_key_constraints=fkcs,
                column_properties=col_props,
                queryable_source=self.queryable_source if self.queryable_source else self.sa_table,
            )

    def filter(
        self,
        dbm: DBMetaInfo,
        meta: MetaData,
        table_selection: ExplicitTableSelection | None = None,
        column_selection: ExplicitColumnSelection | None = None,
    ) -> Self | tuple[Self, Callable[[DBMetaInfo], ...]]:
        tm = self.filter_shallow(column_selection=ExplicitSelectionUtils.relevant_col_set(self, column_selection))

        valid_fks = [
            fkc for fkc in tm.foreign_key_constraints if fkc.is_still_valid(dbm, tm, table_selection, column_selection)
        ]

        new_sa = sa.Table(
            self.name, meta, *(sa.Column(n, tm.sa_table.c[n].type) for n in tm.columns), schema=self.schema_name
        )

        new_tm = self.from_sa_table(new_sa, self.queryable_source, default_schema=dbm.default_schema)

        fixme = None
        if valid_fks:

            def fixme(new_dbm):
                new_tm.sa_table.foreign_key_constraints.update(
                    sa_fkc for fkc in valid_fks if (sa_fkc := fkc.to_sa_constraint(new_dbm)) is not None
                )

        return new_tm, fixme


class DBMetaInfoBase(pydantic.BaseModel):
    """
    This model represents the metadata of a relational database via a structured collection of table metadata.
    It is serializable and can be used for exchange.
    """

    db_structure: dict[SchemaName, dict[TableName, TableMetaInfoBase]]

    @cached_property
    def tables(self) -> dict[ShortTableIdentifier, TableMetaInfoBase]:
        return {
            tm.short_table_identifier: tm
            for schema, tables in self.db_structure.items()
            for table, tm in tables.items()
        }


class DBMetaInfo(DBMetaInfoBase):
    """
    This model represents the metadata of a relational database via a structured collection of table metadata.
    It extends the base model with additional DB metadata, in particular a SQLAlchemy `MetaData` object.
    It is therefore not serializable.

    It can be derived from SQLAlchemy metadata such as a list of `Tables` or a `MetaData` object.
    """

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    db_structure: dict[SchemaName, dict[TableName, TableMetaInfo]]
    default_schema: SchemaName
    sa_meta: MetaData

    @cached_property
    def tables(self) -> dict[ShortTableIdentifier, TableMetaInfo]:
        return {
            tm.short_table_identifier: tm
            for schema, tables in self.db_structure.items()
            for table, tm in tables.items()
        }

    @classmethod
    def from_sa_tables(cls, default_schema: SchemaName, *tables: Table) -> Self:
        db_structure = {}
        meta = sa.MetaData()
        for t in tables:
            meta._add_table(t.name, t.schema, t)  # TODO not so clean
            tm = TableMetaInfo.from_sa_table(t, default_schema=default_schema)
            schema = tm.schema_name
            if schema not in db_structure:
                db_structure[schema] = {}
            db_structure[schema][tm.name] = tm

        return cls(db_structure=db_structure, default_schema=default_schema, sa_meta=meta)

    @classmethod
    def from_sa_meta(cls, meta: MetaData, default_schema: SchemaName) -> Self:
        # note that the connection to the original metadata object is lost in the latest change
        return cls.from_sa_tables(default_schema, *meta.tables.values())

    def search_table(self, schema: SchemaName, table: TableName) -> TableMetaInfo | None:
        return self.db_structure.get(schema, {}).get(table, None)

    def filter_shallow(
        self,
        table_selection: ExplicitTableSelection | None = None,
        column_selection: ExplicitColumnSelection | None = None,
    ) -> Self:
        if table_selection is None:
            return self.model_copy(deep=True)
        else:
            return self.__class__(
                db_structure={
                    schema: {
                        table_name: tm.filter_shallow(ExplicitSelectionUtils.relevant_col_set(tm, column_selection))
                        for table_name, tm in tables.items()
                        if ExplicitSelectionUtils.table_survives(tm, table_selection)
                    }
                    for schema, tables in self.db_structure.items()
                },
                default_schema=self.default_schema,
                sa_meta=self.sa_meta,
            )

    def filter(
        self,
        table_selection: ExplicitTableSelection | None = None,
        column_selection: ExplicitColumnSelection | None = None,
    ) -> Self:
        if table_selection is None:
            return self.model_copy(deep=True)
        else:
            meta = MetaData()
            filtered_tms = {
                schema: {
                    table_name: tm.filter(self, meta, table_selection, column_selection)
                    for table_name, tm in tables.items()
                    if ExplicitSelectionUtils.table_survives(tm, table_selection)
                }
                for schema, tables in self.db_structure.items()
            }
            new_dbm = self.__class__(
                db_structure={
                    schema: {table_name: tm for table_name, (tm, _) in filter_results.items()}
                    for schema, filter_results in filtered_tms.items()
                },
                default_schema=self.default_schema,
                sa_meta=meta,
            )
            for filter_results in filtered_tms.values():
                for _, fixme in filter_results.values():
                    if fixme:
                        fixme(new_dbm)
            return new_dbm
