from __future__ import annotations

from enum import StrEnum

import pydantic
import sqlalchemy as sa
from pydantic import ConfigDict
from sqlalchemy import FromClause

from mitm_tooling.definition import MITM, ConceptName, RelationName, TypeName

from ..common import MITMRepresentationError

TableName = str
SchemaName = str
ShortTableIdentifier = tuple[SchemaName, TableName]
QualifiedTableName = str
Queryable = FromClause


class SQLRepresentationError(MITMRepresentationError):
    pass


class SQLRepresentationSchemaUpdateError(SQLRepresentationError):
    pass


class SQLRepresentationMetaUpdateError(SQLRepresentationError):
    pass


class SQLRepresentationInstanceUpdateError(SQLRepresentationError):
    pass


class SQLRepresentationDropError(SQLRepresentationError):
    pass


class HeaderMetaTableName(StrEnum):
    KeyValue = 'header_meta_key_value'
    HeaderMetaDefinition = 'header_meta_definition'
    Types = 'header_meta_types'
    TypeAttributes = 'header_meta_type_attributes'


class HeaderMetaTables(pydantic.BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    key_value: sa.Table
    types: sa.Table
    type_attributes: sa.Table


class ViewProperties(pydantic.BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: TableName
    selectable: sa.Selectable
    cascade_on_drop: bool = False
    replace: bool = False
    is_type_dependant: bool = False


ColumnsDict = dict[RelationName, sa.Column]
ViewsDict = dict[TableName, tuple[sa.Table, ViewProperties]]
ConceptTablesDict = dict[ConceptName, sa.Table]
ConceptTypeTablesDict = dict[ConceptName, dict[TypeName, sa.Table]]


class SQLRepresentationSchema(pydantic.BaseModel):
    """
    This model represents the SQL representation of a MITM data set via a collection of SQLAlchemy tables and views.
    It is not serializable itself but can be generated from a `Header` object (i.e., pure type information).
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, strict=False)

    mitm: MITM
    sa_meta: sa.MetaData
    meta_tables: HeaderMetaTables | None = None
    concept_tables: ConceptTablesDict = pydantic.Field(default_factory=ConceptTablesDict)
    type_tables: ConceptTypeTablesDict = pydantic.Field(default_factory=ConceptTypeTablesDict)
    views: ViewsDict = pydantic.Field(default_factory=ViewsDict)

    def get_concept_table(self, concept: ConceptName) -> sa.Table | None:
        return self.concept_tables.get(concept)

    def get_type_table(self, concept: ConceptName, type_name: TypeName) -> sa.Table | None:
        return self.type_tables.get(concept, {}).get(type_name)

    @property
    def view_tables(self) -> dict[str, sa.Table]:
        return {k: t for k, (t, _) in self.views.items()}

    @property
    def tables_list(self) -> list[sa.Table]:
        return list(self.sa_meta.tables.values()) + list(self.view_tables.values())
