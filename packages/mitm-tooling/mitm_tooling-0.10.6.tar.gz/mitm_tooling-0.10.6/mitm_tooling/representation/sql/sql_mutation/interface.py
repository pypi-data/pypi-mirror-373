from __future__ import annotations

from collections.abc import Callable

from mitm_tooling.utilities.sql_utils import AnyDBBind

from ...df import TypedMITMDataFrameStream
from ...intermediate.header import Header
from ..common import (
    SQLRepresentationInstanceUpdateError,
)
from ..sql_representation import SQLRepresentationSchema, mk_sql_rep_schema
from .drop_instances import drop_type_instances
from .insert_instances import SQLRepInsertionResult, insert_instances
from .update_metatables import update_meta_data
from .update_schema import create_db_schema, drop_db_schema, migrate_schema


def create_schema(
    bind: AnyDBBind,
    gen_sql_rep_schema: Callable[[], SQLRepresentationSchema],
) -> None:
    """
    Create the mitm database schema defined by the given SQL representation schema factory.

    Note that if this function is called with a `bind` of type `Connection` (as opposed to a `Engine`),
    a manual commit is required after calling it to persist the changes.
    Internally, all changes are performed within nested transactions.

    :param bind: a bind to the database to insert into
    :param gen_sql_rep_schema: a factory for the SQL representation schema to use
    :return:
    """

    sql_rep_schema = gen_sql_rep_schema()
    create_db_schema(bind, sql_rep_schema)


def drop_schema(
    bind: AnyDBBind,
    gen_sql_rep_schema: Callable[[], SQLRepresentationSchema],
) -> None:
    """
    Drop the mitm database schema defined by the given SQL representation schema factory.

    Note that if this function is called with a `bind` of type `Connection` (as opposed to a `Engine`),
    a manual commit is required after calling it to persist the changes.
    Internally, all changes are performed within nested transactions.

    :param bind: a bind to the database to insert into
    :param gen_sql_rep_schema: a factory for the SQL representation schema to use
    :return:
    """
    sql_rep_schema = gen_sql_rep_schema()
    drop_db_schema(bind, sql_rep_schema)


def insert_data(
    bind: AnyDBBind,
    gen_header: Callable[[], Header],
    gen_sql_rep_schema: Callable[[Header], SQLRepresentationSchema] = lambda h: mk_sql_rep_schema(h),
    gen_instances: Callable[[], TypedMITMDataFrameStream] = lambda: (),
) -> SQLRepInsertionResult:
    """
    Insert a stream of MITM dataframes into a relational database, with tables (and views) defined by the given SQL representation schema.
    The schema is first created and then the data is inserted.
    Finally, the meta-tables are updated with the header information.

    Note that if this function is called with a `bind` of type `Connection` (as opposed to a `Engine`),
    a manual commit is required after calling it to persist the changes.
    Internally, all changes are performed within nested transactions.

    :param bind: a bind to the database to insert into
    :param gen_header: a factory for a header to use for the SQL representation schema
    :param gen_sql_rep_schema: a factory for the SQL representation schema to use
    :param gen_instances: a factory for a stream of (typed) instances to insert
    :return: a summary of the inserted instances
    """

    header = gen_header()
    sql_rep_schema = gen_sql_rep_schema(header)
    create_db_schema(bind, sql_rep_schema)
    insertion_result = insert_instances(bind, sql_rep_schema, gen_instances())
    update_meta_data(bind, sql_rep_schema, header)
    return insertion_result


def append_data(
    bind: AnyDBBind,
    gen_sql_rep_schema: Callable[[], SQLRepresentationSchema],
    gen_instances: Callable[[], TypedMITMDataFrameStream] = lambda: (),
) -> SQLRepInsertionResult:
    """
    Append a stream of MITM dataframes into a relational database, with tables (and views) defined by the given SQL representation schema.
    This assumes that the schema is already created. In particular, this implies that the instances to be inserted cannot be of any type not yet present in the schema.

    Note that if this function is called with a `bind` of type `Connection` (as opposed to a `Engine`),
    a manual commit is required after calling it to persist the changes.
    Internally, all changes are performed within nested transactions.

    :param bind: a bind to the database to insert into
    :param gen_sql_rep_schema: a factory for the SQL representation schema to use
    :param gen_instances: a factory for a stream of (typed) instances to insert
    :return: a summary of the inserted instances
    """

    sql_rep_schema = gen_sql_rep_schema()
    insertion_result = insert_instances(bind, sql_rep_schema, gen_instances())
    return insertion_result


def drop_data(
    bind: AnyDBBind,
    gen_sql_rep_schema: Callable[[], SQLRepresentationSchema],
):
    """
    Drop all instances from all tables, using the given ´gen_sql_rep_schema`.
    This preserves the type tables and meta-tables themselves.

    Note that if this function is called with a `bind` of type `Connection` (as opposed to a `Engine`),
    a manual commit is required after calling it to persist the changes.
    Internally, all changes are performed within nested transactions.

    :param bind: a bind to the database to insert into
    :param gen_sql_rep_schema: a factory for the SQL representation schema to use
    :return:
    """

    sql_rep_schema = gen_sql_rep_schema()
    try:
        drop_type_instances(bind, sql_rep_schema)
    except Exception as e:
        raise SQLRepresentationInstanceUpdateError('Dropping of all instances failed') from e


def mutate_schema(
    bind: AnyDBBind,
    gen_current_header: Callable[[], Header],
    gen_target_header: Callable[[], Header],
    gen_current_sql_rep_schema: Callable[[Header], SQLRepresentationSchema] = lambda h: mk_sql_rep_schema(h),
    gen_target_sql_rep_schema: Callable[[Header], SQLRepresentationSchema] = lambda h: mk_sql_rep_schema(h),
) -> None:
    """
    Mutate the header of a mitm db (relational database in canonical mitm format) to a target header.
    Migrating the derived SQL representation schema entails the following steps:

    1. drop all views that depend on types from the current header
    2. drop all types from the current header
    3. migrate the existing tables to reflect type changes and create new tables for new types
    4. recreate all type-dependent views
    5. update the meta-tables with the new header information

    Note that if this function is called with a `bind` of type `Connection` (as opposed to a `Engine`),
    a manual commit is required after calling it to persist the changes.
    Internally, all changes are performed within nested transactions.

    :param bind: a bind to the database to insert into
    :param gen_current_header: a factory for creating the current header from which to migrate
    :param gen_target_header: a factory for creating the target header to which to migrate
    :param gen_current_sql_rep_schema: a factory for creating the current SQL representation schema from the current header
    :param gen_target_sql_rep_schema: a factory for creating the target SQL representation schema from the target header
    :return:
    """
    current_header = gen_current_header()
    new_header = gen_target_header()

    current_sql_rep_schema = gen_current_sql_rep_schema(current_header)
    target_sql_rep_schema = gen_target_sql_rep_schema(new_header)

    migrate_schema(bind, current_header, new_header, current_sql_rep_schema, target_sql_rep_schema)
