from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pydantic
import sqlalchemy as sa
from pydantic import Field

from mitm_tooling.data_types import SQL_DataType, get_sa_sql_type
from mitm_tooling.representation.sql import SchemaName, ShortTableIdentifier, TableName

from .table_identifiers import LocalTableIdentifier

if TYPE_CHECKING:
    from .virtual_view import VirtualDB, VirtualView

logger = logging.getLogger(__name__)


class TypedRawQuery(pydantic.BaseModel):
    dialect: str
    compiled_sql: str
    columns: tuple[str, ...]
    column_dtypes: tuple[SQL_DataType, ...]

    @classmethod
    def compile_from_clause(cls, clause: sa.FromClause, dialect: sa.Dialect) -> str:
        compiled = clause.compile(dialect=dialect, compile_kwargs={'literal_binds': True})
        contains_binds = len(compiled.binds) > 0
        if contains_binds:
            logger.warning(f'Compiled query contains binds:\n{compiled}')
        return str(compiled)

    def to_from_clause(self) -> sa.FromClause:
        cols = [sa.Column(c, get_sa_sql_type(dt)) for c, dt in zip(self.columns, self.column_dtypes, strict=False)]
        return sa.text(self.compiled_sql).columns(*cols).subquery()


class CompiledVirtualView(TypedRawQuery):
    name: TableName
    schema_name: SchemaName

    @property
    def table_identifier(self) -> LocalTableIdentifier:
        return LocalTableIdentifier(name=self.name, schema=self.schema_name)

    def to_virtual_view(self, meta: sa.MetaData, delete_if_exists: bool = True) -> VirtualView:
        return VirtualView.from_from_clause(
            self.name, self.to_from_clause(), meta, schema=self.schema_name, delete_if_exists=delete_if_exists
        )


class CompiledVirtualDB(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    compiled_virtual_views: list[CompiledVirtualView] = Field(default_factory=list)

    @pydantic.computed_field(repr=False)
    @property
    def views(self) -> dict[ShortTableIdentifier, CompiledVirtualView]:
        return {cvv.table_identifier.as_tuple(): cvv for cvv in self.compiled_virtual_views}

    def to_virtual_db(self) -> VirtualDB:
        vdb = VirtualDB()
        for cvv in self.compiled_virtual_views:
            vdb.put_view(cvv.to_virtual_view(vdb.sa_meta))
        return vdb
