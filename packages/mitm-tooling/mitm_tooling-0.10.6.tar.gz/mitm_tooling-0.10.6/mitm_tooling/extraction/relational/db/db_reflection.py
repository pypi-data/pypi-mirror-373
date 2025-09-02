from collections.abc import Collection
from typing import Any

import pydantic
from sqlalchemy import MetaData, inspect

from mitm_tooling.representation.sql import SchemaName
from mitm_tooling.utilities.sql_utils import AnyDBBind, qualify, use_db_bind

from ..data_models import DBMetaInfo, TableMetaInfo


class TableDoesNotExist(Exception):
    pass


class AdditionalMeta(pydantic.BaseModel):
    default_schema: SchemaName


def sa_reflect(
    bind: AnyDBBind,
    meta: MetaData | None = None,
    allowed_schemas: Collection[str] | None = None,
    reflect_kwargs: dict[str, Any] | None = None,
) -> tuple[MetaData, AdditionalMeta]:
    with use_db_bind(bind) as conn:
        inspector = inspect(conn)
        schemas = inspector.get_schema_names()

        kwargs = dict(resolve_fks=True, views=True, extend_existing=True, autoload_replace=True)
        if reflect_kwargs:
            kwargs |= reflect_kwargs

        meta = meta if meta else MetaData()
        if schemas:
            for schema in schemas:
                if not allowed_schemas or schema in allowed_schemas:
                    meta.reflect(conn, schema=schema, **kwargs)
        else:
            meta.reflect(conn, **kwargs)

        return meta, AdditionalMeta(
            default_schema=(
                inspector.default_schema_name if inspector.default_schema_name else next(iter(meta._schemas))
            )
        )


def derive_table_meta_info(
    sa_meta: MetaData, name: str, schema: SchemaName | None = None, default_schema: SchemaName | None = None
) -> TableMetaInfo:
    qualified = qualify(table=name, schema=schema)
    try:
        t = sa_meta.tables[qualified]
        return TableMetaInfo.from_sa_table(t, default_schema=default_schema)
    except KeyError as e:
        raise TableDoesNotExist from e


def derive_db_meta_info(sa_meta: MetaData, default_schema: SchemaName) -> DBMetaInfo:
    return DBMetaInfo.from_sa_meta(sa_meta, default_schema=default_schema)


def create_table_meta(bind: AnyDBBind, name: str, schema: SchemaName | None = None) -> TableMetaInfo:
    sa_meta, a_meta = sa_reflect(bind)
    return derive_table_meta_info(sa_meta, name, schema=schema, default_schema=a_meta.default_schema)


def create_db_meta(bind: AnyDBBind) -> DBMetaInfo:
    sa_meta, a_meta = sa_reflect(bind)
    return derive_db_meta_info(sa_meta, default_schema=a_meta.default_schema)
