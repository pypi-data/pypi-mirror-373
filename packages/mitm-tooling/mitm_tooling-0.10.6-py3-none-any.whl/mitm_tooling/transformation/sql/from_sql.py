import sqlalchemy as sa

from mitm_tooling.extraction.relational.data_models import DBMetaInfo
from mitm_tooling.extraction.relational.db import sa_reflect
from mitm_tooling.representation.sql import SQL_REPRESENTATION_DEFAULT_SCHEMA, SQLRepresentationSchema


def db_engine_into_db_meta(engine: sa.Engine) -> DBMetaInfo:
    """
    Introspect an SQLAlchemy engine and return a `DBMetaInfo` object.
    """
    sa_meta, more_meta = sa_reflect(engine)
    return DBMetaInfo.from_sa_meta(sa_meta, default_schema=more_meta.default_schema)


def sql_rep_schema_into_db_meta(
    sql_rep_schema: SQLRepresentationSchema, default_schema: str = SQL_REPRESENTATION_DEFAULT_SCHEMA
) -> DBMetaInfo:
    """
    Derive a `DBMetaInfo` object from an `SQLRepresentationSchema`.
    """
    return DBMetaInfo.from_sa_tables(default_schema, *sql_rep_schema.tables_list)
