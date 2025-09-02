from __future__ import annotations

from typing import TYPE_CHECKING, Self

import pydantic
import sqlalchemy as sa
from pydantic import Field

from mitm_tooling.representation.sql import SchemaName, ShortTableIdentifier, TableName
from mitm_tooling.utilities.sql_utils import qualify

from .db_meta import DBMetaInfo, TableMetaInfo, TableMetaInfoBase

if TYPE_CHECKING:
    from .compiled import CompiledVirtualDB, CompiledVirtualView

VIRTUAL_DB_DEFAULT_SCHEMA = 'virtual'


class VirtualViewBase(pydantic.BaseModel):
    table_meta: TableMetaInfoBase


class VirtualView(VirtualViewBase):
    """
    This model represents a virtual view in a relational database, i.e., a selectable SQL query in combination with its column metadata.
    As it contains SQLAlchemy objects, it is not serializable.

    Given a specific SQL dialect, it can also be compiled into a serializable `CompiledVirtualView`.
    """

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    table_meta: TableMetaInfo
    from_clause: sa.FromClause
    sa_table: sa.Table

    @classmethod
    def from_from_clause(
        cls,
        name: str,
        from_clause: sa.FromClause,
        meta: sa.MetaData,
        schema: SchemaName = 'virtual',
        delete_if_exists: bool = True,
    ) -> Self | None:
        cols = [sa.Column(n, c.type, primary_key=c.primary_key) for n, c in from_clause.columns.items()]

        if (t := meta.tables.get(qualify(schema=schema, table=name), None)) is not None:
            if delete_if_exists:
                meta.remove(t)
            else:
                return None

        virtual_table = sa.Table(name, meta, *cols, schema=schema)
        tm = TableMetaInfo.from_sa_table(virtual_table, queryable_source=from_clause, default_schema=schema)
        return cls(table_meta=tm, from_clause=from_clause, sa_table=virtual_table)

    def update_table_meta(self) -> None:
        self.table_meta = TableMetaInfo.from_sa_table(
            self.sa_table, queryable_source=self.from_clause, default_schema=self.sa_table.schema
        )

    def as_compiled(self, dialect: sa.Dialect) -> CompiledVirtualView:
        from .compiled import CompiledVirtualView, TypedRawQuery

        compiled_sql = TypedRawQuery.compile_from_clause(self.from_clause, dialect)
        tm = self.table_meta
        return CompiledVirtualView(
            name=tm.name,
            schema_name=tm.schema_name,
            dialect=dialect.name,
            compiled_sql=compiled_sql,
            columns=tuple(tm.columns),
            column_dtypes=tuple(tm.sql_column_types),
        )


class VirtualDBBase(pydantic.BaseModel):
    virtual_views: dict[SchemaName, dict[TableName, VirtualViewBase]] = Field(default_factory=dict)


class VirtualDB(VirtualDBBase):
    """
    This model represents a virtual database via a structured collection of virtual views.
    As it contains SQLAlchemy objects, it is not serializable.

    It can be mutated by adding and removing virtual views.
    Given a specific SQL dialect, it can also be compiled into a serializable `CompiledVirtualDB`, which in turn can be used as a `VirtualDBCreation` in a `StandaloneDBMapping`.
    """

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    virtual_views: dict[SchemaName, dict[TableName, VirtualView]] = Field(default_factory=dict)
    sa_meta: sa.MetaData = Field(default_factory=lambda: sa.MetaData(schema='virtual'))

    @pydantic.computed_field(repr=False)
    @property
    def views(self) -> dict[ShortTableIdentifier, VirtualView]:
        return {
            vv.table_meta.short_table_identifier: vv
            for schema, views in self.virtual_views.items()
            for view, vv in views.items()
        }

    def put_view(self, vv: VirtualView):
        schema = vv.table_meta.schema_name
        if schema not in self.virtual_views:
            self.virtual_views[schema] = {}
        self.virtual_views[schema][vv.table_meta.name] = vv

    def get_view(self, schema: SchemaName, view: TableName) -> VirtualView | None:
        return self.virtual_views.get(schema, {}).get(view, None)

    def drop_view(self, schema: SchemaName, view: TableName):
        tm = self.get_view(schema, view)
        if tm is not None:
            self.sa_meta.remove(tm.sa_table)
            del self.virtual_views[schema][view]
            if len(self.virtual_views[schema]) == 0:
                del self.virtual_views[schema]

    def update_views(self) -> None:
        for vv in self.views.values():
            vv.update_table_meta()

    def to_db_meta_info(self) -> DBMetaInfo:
        return DBMetaInfo(
            db_structure={
                schema: {view: vv.table_meta for view, vv in views.items()}
                for schema, views in self.virtual_views.items()
            },
            sa_meta=self.sa_meta,
            default_schema=VIRTUAL_DB_DEFAULT_SCHEMA,
        )

    def as_compiled(self, dialect: sa.Dialect) -> CompiledVirtualDB:
        from .compiled import CompiledVirtualDB

        return CompiledVirtualDB(compiled_virtual_views=[vv.as_compiled(dialect) for vv in self.views.values()])
