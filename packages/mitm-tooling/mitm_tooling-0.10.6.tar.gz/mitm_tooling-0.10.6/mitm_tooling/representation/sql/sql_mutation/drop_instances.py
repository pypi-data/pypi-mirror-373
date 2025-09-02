from __future__ import annotations

from collections.abc import Iterable

from mitm_tooling.definition import ConceptName, TypeName
from mitm_tooling.utilities.sql_utils import AnyDBBind, use_nested_conn

from ..common import (
    SQLRepresentationInstanceUpdateError,
)
from ..sql_representation import SQLRepresentationSchema
from .drop_types import _drop_types


def drop_type_instances(
    bind: AnyDBBind,
    sql_rep_schema: SQLRepresentationSchema,
    types_to_drop: Iterable[tuple[ConceptName, TypeName]] | None = None,
) -> None:
    """
    Drop all instances of the given types from the mitm database given by the `sql_rep_schema`.

    :param bind: a bind to the database to insert into
    :param sql_rep_schema: the SQL representation schema to use
    :param types_to_drop: an iterable of (concept, type_name) tuples to drop instances of
    :return:
    """
    if types_to_drop is None:
        types_to_drop = [
            (c, type_name) for c, type_tables in sql_rep_schema.type_tables.items() for type_name in type_tables
        ]
    try:
        with use_nested_conn(bind) as conn:
            _drop_types(conn, sql_rep_schema, types_to_drop, instances_only=True)
    except Exception as e:
        raise SQLRepresentationInstanceUpdateError('Dropping of instances of types failed') from e
