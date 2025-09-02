from __future__ import annotations

import enum
from typing import TYPE_CHECKING, Annotated, Self

import pydantic
from pydantic import AfterValidator, Field

from mitm_tooling.representation.sql import SchemaName, ShortTableIdentifier, TableName

if TYPE_CHECKING:
    from .db_meta import DBMetaInfo, TableMetaInfo


class SourceDBType(enum.StrEnum):
    OriginalDB = 'original'
    WorkingDB = 'working'
    VirtualDB = 'virtual'


LongTableIdentifier = tuple[SourceDBType, SchemaName, TableName]


class LocalTableIdentifier(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(validate_by_name=True)

    name: TableName
    schema_name: SchemaName = Field(alias='schema', serialization_alias='schema', default='main')

    def as_tuple(self) -> ShortTableIdentifier:
        return self.schema_name, self.name

    @classmethod
    def from_any(cls, arg: dict | ShortTableIdentifier | LongTableIdentifier | Self | TableIdentifier) -> Self:
        ret = None
        if isinstance(arg, tuple):
            match len(arg):
                case 2:
                    ret = cls(schema=arg[0], name=arg[1])
        elif isinstance(arg, dict):
            ret = cls.model_validate(arg)
        elif isinstance(arg, TableIdentifier):
            ret = cls(schema=arg.schema_name, name=arg.name)
        elif isinstance(arg, LocalTableIdentifier):
            ret = arg
        return ret

    @classmethod
    def resolve_id(cls, table_identifier: AnyTableIdentifier, db_meta: DBMetaInfo) -> TableMetaInfo | None:
        return cls.from_any(table_identifier).resolve(db_meta)

    def resolve(self, db_meta: DBMetaInfo) -> TableMetaInfo | None:
        tm = db_meta.search_table(self.schema_name, self.name)
        return tm


class TableIdentifier(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(validate_by_name=True, validate_by_alias=True)

    source: SourceDBType = Field(default=SourceDBType.OriginalDB)
    schema_name: SchemaName = Field(alias='schema', serialization_alias='schema', default='main')
    name: TableName

    def as_tuple(self) -> LongTableIdentifier:
        return self.source, self.schema_name, self.name

    @classmethod
    def check_equal(cls, left: AnyTableIdentifier, right: AnyTableIdentifier):
        return TableIdentifier.from_any(left).as_tuple() == TableIdentifier.from_any(right).as_tuple()

    @classmethod
    def from_any(cls, arg: ShortTableIdentifier | LongTableIdentifier | Self | dict) -> Self:
        ret = None
        if isinstance(arg, tuple):
            match len(arg):
                case 2:
                    ret = cls(schema=arg[0], name=arg[1])
                case 3:
                    ret = cls(source=SourceDBType(arg[0]), schema=arg[1], name=arg[2])
        elif isinstance(arg, dict):
            ret = cls.model_validate(arg)
        elif isinstance(arg, TableIdentifier):
            ret = arg
        return ret

    @classmethod
    def resolve_id(
        cls, table_identifier: AnyTableIdentifier, db_metas: dict[SourceDBType, DBMetaInfo]
    ) -> TableMetaInfo | None:
        return cls.from_any(table_identifier).resolve(db_metas)

    def resolve(self, db_metas: dict[SourceDBType, DBMetaInfo]) -> TableMetaInfo | None:
        dbm = db_metas.get(self.source, None)
        if dbm is not None:
            tm = dbm.search_table(self.schema_name, self.name)
            return tm
        return None


AnyTableIdentifier = Annotated[
    TableIdentifier | LongTableIdentifier | ShortTableIdentifier, AfterValidator(lambda v: TableIdentifier.from_any(v))
]

AnyLocalTableIdentifier = Annotated[
    LocalTableIdentifier | ShortTableIdentifier, AfterValidator(lambda v: LocalTableIdentifier.from_any(v))
]
