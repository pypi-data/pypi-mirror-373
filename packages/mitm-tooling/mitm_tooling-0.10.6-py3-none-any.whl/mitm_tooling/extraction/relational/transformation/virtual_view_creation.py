import logging
from collections.abc import Callable
from functools import cached_property
from typing import Self

import pydantic
import sqlalchemy as sa
from pydantic import Field

from mitm_tooling.representation.sql import SchemaName, TableName

from ..data_models import (
    CompiledVirtualDB,
    CompiledVirtualView,
    DBMetaInfo,
    Queryable,
    SourceDBType,
    TableIdentifier,
    VirtualDB,
    VirtualView,
)
from ..transformation.db_transformation import (
    ColumnNotFoundException,
    InvalidQueryException,
    TableCreations,
    TableNotFoundException,
    TableTransforms,
    TransformationError,
)
from .db_transformation import RawCompiled

logger = logging.getLogger(__name__)


class VirtualViewCreation(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(validate_by_name=True)

    name: TableName
    schema_name: SchemaName = Field(alias='schema', default='virtual')
    table_creation: TableCreations
    transforms: list[TableTransforms] | None = None

    @cached_property
    def table_identifier(self) -> TableIdentifier:
        return TableIdentifier(source=SourceDBType.VirtualDB, schema=self.schema_name, name=self.name)

    @classmethod
    def from_compiled(cls, cvv: CompiledVirtualView):
        return cls(name=cvv.name, schema=cvv.schema_name, table_creation=RawCompiled(typed_query=cvv))

    @classmethod
    def from_virtual_view(cls, virtual_view: VirtualView, dialect: sa.Dialect) -> Self:
        return cls.from_compiled(virtual_view.as_compiled(dialect))

    def make_queryable(self, db_metas: dict[SourceDBType, DBMetaInfo]) -> Queryable:
        from_clause = self.table_creation.make_from_clause(db_metas)

        if transforms := self.transforms:
            for t in transforms:
                from_clause = t.transform_from_clause(from_clause)
        return from_clause

    def apply(
        self,
        db_metas: dict[SourceDBType, DBMetaInfo],
        override_if_exists: bool = False,
        queryable_verifier: Callable[[Queryable], bool] | None = None,
    ) -> VirtualView:
        try:
            from_clause = self.make_queryable(db_metas)

            if queryable_verifier is not None:
                try:
                    if not queryable_verifier(from_clause):
                        raise InvalidQueryException
                except Exception as e:
                    raise InvalidQueryException(
                        f'Virtual view query: {from_clause} was not executable on the connected DB.'
                    ) from e

            vv = VirtualView.from_from_clause(
                self.name,
                from_clause,
                db_metas[SourceDBType.VirtualDB].sa_meta,
                schema=self.schema_name,
                delete_if_exists=override_if_exists,
            )

            return vv
        except (TransformationError, TableNotFoundException, ColumnNotFoundException, InvalidQueryException) as e:
            logger.error(f'Error during virtual view creation: {e}')
            raise e


class VirtualDBCreation(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    virtual_view_creations: list[VirtualViewCreation] = Field(default_factory=list)

    @classmethod
    def from_compiled(cls, compiled_vdb: CompiledVirtualDB) -> Self:
        return cls(
            virtual_view_creations=[
                VirtualViewCreation.from_compiled(cvv) for cvv in compiled_vdb.compiled_virtual_views
            ]
        )

    @classmethod
    def from_virtual_db(cls, virtual_db: VirtualDB, dialect: sa.Dialect) -> Self:
        return cls.from_compiled(virtual_db.as_compiled(dialect))

    def apply(
        self,
        original_db_meta: DBMetaInfo,
        override_if_exists: bool = False,
        queryable_verifier: Callable[[Queryable], bool] | None = None,
    ) -> VirtualDB:
        # this method raises if any of the virtual views cannot be created
        vdb = VirtualDB()
        db_metas = {SourceDBType.OriginalDB: original_db_meta}
        for vvc in self.virtual_view_creations:
            db_metas[SourceDBType.VirtualDB] = (
                vdb.to_db_meta_info()
            )  # inefficient but this allows views to depend on each other
            vv = vvc.apply(db_metas, override_if_exists=override_if_exists, queryable_verifier=queryable_verifier)
            if vv is not None:
                vdb.put_view(vv)
        return vdb
