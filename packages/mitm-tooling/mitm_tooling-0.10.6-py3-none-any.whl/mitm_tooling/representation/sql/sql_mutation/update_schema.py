from __future__ import annotations

from collections.abc import Callable

from mitm_tooling.utilities.backports.sqlchemy_sql_views import create_table_as_view, drop_table_as_view
from mitm_tooling.utilities.sql_utils import AnyDBBind, EngineOrConnection, use_nested_conn

from ...intermediate import deltas
from ...intermediate.header import Header
from ..common import (
    SQLRepresentationSchemaUpdateError,
    ViewProperties,
)
from ..sql_representation import SQLRepresentationSchema
from .drop_types import _drop_types
from .update_metatables import update_meta_data


def create_db_schema(bind: EngineOrConnection, sql_rep_schema: SQLRepresentationSchema) -> None:
    try:
        with use_nested_conn(bind) as conn:
            sql_rep_schema.sa_meta.create_all(bind=conn, checkfirst=True)
    except Exception as e:
        raise SQLRepresentationSchemaUpdateError('Creation of SQL schema failed') from e


def drop_db_schema(bind: EngineOrConnection, sql_rep_schema: SQLRepresentationSchema) -> None:
    try:
        with use_nested_conn(bind) as conn:
            sql_rep_schema.sa_meta.drop_all(bind=conn, checkfirst=True)
    except Exception as e:
        raise SQLRepresentationSchemaUpdateError('Dropping of SQL schema failed') from e


def create_views(
    bind: EngineOrConnection,
    sql_rep_schema: SQLRepresentationSchema,
    only: Callable[[ViewProperties], bool] | None = None,
) -> None:
    try:
        with use_nested_conn(bind) as conn:
            for v, vp in sql_rep_schema.views.values():
                if only is None or only(vp):
                    create_table_as_view(conn, vp.selectable, v, replace=vp.replace)
    except Exception as e:
        raise SQLRepresentationSchemaUpdateError('Creation of SQL views failed') from e


def drop_views(
    bind: EngineOrConnection,
    sql_rep_schema: SQLRepresentationSchema,
    only: Callable[[ViewProperties], bool] | None = None,
) -> None:
    try:
        with use_nested_conn(bind) as conn:
            for v, vp in sql_rep_schema.views.values():
                if only is None or only(vp):
                    drop_table_as_view(conn, v, cascade_on_drop=vp.cascade_on_drop)
    except Exception as e:
        raise SQLRepresentationSchemaUpdateError('Dropping of SQL views failed') from e


def migrate_schema(
    bind: AnyDBBind,
    current_header: Header,
    target_header: Header,
    current_sql_rep_schema: SQLRepresentationSchema,
    target_sql_rep_schema: SQLRepresentationSchema,
) -> None:
    diffs = deltas.diff_header(current_header, target_header)
    types_to_drop = [td for td in diffs.type_deltas if td.kind == 'deletion']

    try:
        from .schema_migration import run_ephemeral_migration

        drop_views(bind, current_sql_rep_schema, only=lambda vp: vp.is_type_dependant)

        with use_nested_conn(bind) as conn:
            _drop_types(
                conn,
                current_sql_rep_schema,
                ((td.concept, td.type_name) for td in types_to_drop),
                drop_from_meta_tables=False,
            )

        run_ephemeral_migration(bind, target_sql_rep_schema.sa_meta)

        create_views(bind, target_sql_rep_schema, only=lambda vp: vp.is_type_dependant)

        update_meta_data(bind, target_sql_rep_schema, target_header)
        # conn.commit()
    except Exception as e:
        raise SQLRepresentationSchemaUpdateError('Schema migration failed') from e
