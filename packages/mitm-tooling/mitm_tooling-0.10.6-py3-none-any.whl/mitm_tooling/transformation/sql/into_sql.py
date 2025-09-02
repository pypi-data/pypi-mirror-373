import sqlalchemy as sa
from pydantic import AnyUrl

from mitm_tooling.extraction.relational.mapping import Exportable
from mitm_tooling.representation.df import MITMDataFrames, TypedMITMDataFrameStream
from mitm_tooling.representation.intermediate import Header, MITMData
from mitm_tooling.representation.sql import (
    SchemaName,
    SQLRepInsertionResult,
    SQLRepresentationSchema,
    append_data,
    insert_data,
    mk_sql_rep_schema,
)
from mitm_tooling.utilities.io_utils import FilePath
from mitm_tooling.utilities.sql_utils import AnyDBBind, EngineOrConnection, create_sa_engine


def insert_mitm_data(
    bind: EngineOrConnection,
    mitm_data: MITMData,
    schema_name: SchemaName | None = None,
) -> SQLRepInsertionResult:
    """
    Insert `MITMData` instances into a relational database, using the given `SQLRepresentationSchema`.
    The database schema, including tables, is first created via DDL, then the data is inserted via INSERT statements.

    See also `insert_data`.
    """

    def instances() -> TypedMITMDataFrameStream:
        from mitm_tooling.transformation.df import mitm_data_into_mitm_dataframes

        return mitm_data_into_mitm_dataframes(mitm_data).as_streaming().typed_stream()

    return insert_data(
        bind, lambda: mitm_data.header, lambda h: mk_sql_rep_schema(h, target_schema=schema_name), instances
    )


def insert_mitm_dataframes(
    bind: EngineOrConnection,
    mitm_dataframes: MITMDataFrames,
    schema_name: SchemaName | None = None,
) -> SQLRepInsertionResult:
    """
    Insert `MITMDataFrames` instances into a relational database, using the given `SQLRepresentationSchema`.
    The database schema, including tables, is first created via DDL, then the data is inserted via INSERT statements.

    See also `insert_data`.
    """

    def instances() -> TypedMITMDataFrameStream:
        return mitm_dataframes.as_streaming().typed_stream()

    return insert_data(
        bind, lambda: mitm_dataframes.header, lambda h: mk_sql_rep_schema(h, target_schema=schema_name), instances
    )


def insert_exportable(
    target: AnyDBBind,
    source: AnyDBBind,
    exportable: Exportable,
    target_schema: SchemaName | None = None,
    stream_data: bool = False,
) -> SQLRepInsertionResult:
    """
    Insert instances from the `source` database into the `target` database, using the ETL-pipeline defined by the `Exportable`.
    First, the database schema, including tables, as defined by the `SQLRepresentationSchema` is created on the target database.
    Then, the data is queried from the source and is inserted into the target.
    Depending on the `stream_data` parameter, the data is inserted in batches or all at once.

    See also `insert_data`.
    """

    def header() -> Header:
        return exportable.generate_header(source)

    def instances() -> TypedMITMDataFrameStream:
        from mitm_tooling.transformation.df import exportable_to_typed_mitm_dataframes_stream

        return exportable_to_typed_mitm_dataframes_stream(source, exportable, stream_data=stream_data)

    return insert_data(target, header, lambda h: mk_sql_rep_schema(h, target_schema=target_schema), instances)


def append_exportable(
    target: AnyDBBind,
    source: AnyDBBind,
    exportable: Exportable,
    target_schema: SchemaName | None = None,
    stream_data: bool = False,
) -> SQLRepInsertionResult:
    """
    Insert instances from the `source` database into the `target` database, using the ETL-pipeline defined by the `Exportable`.
    In contrast to `insert_exportable`, this function assumes that the schema is already created.
    As a first step, the `SQLRepresentationSchema` is derived from the `Header` of the target database.
    Then, the data is queried from the source and is inserted into the target.
    Depending on the `stream_data` parameter, the data is incrementally queried and then inserted in chunks or first fully loaded and then inserted.

    See also `append_data`.
    """

    def sql_rep_schema() -> SQLRepresentationSchema:
        from mitm_tooling.transformation.sql import mitm_db_into_header

        h = mitm_db_into_header(target, override_schema=target_schema)
        return mk_sql_rep_schema(h, target_schema=target_schema)

    def instances() -> TypedMITMDataFrameStream:
        from mitm_tooling.transformation.df import exportable_to_typed_mitm_dataframes_stream

        return exportable_to_typed_mitm_dataframes_stream(source, exportable, stream_data=stream_data)

    return append_data(target, sql_rep_schema, instances)


def mk_sqlite(mitm_data: MITMData, file_path: FilePath | None = ':memory:', autoclose: bool = True) -> sa.Engine:
    """
    Insert `mitm_data` into a SQLite database. It is created if it does not exist. Uses `insert_mitm_data`.
    """

    engine = create_sa_engine(AnyUrl(f'sqlite:///{str(file_path)}'), poolclass=sa.StaticPool)
    insert_mitm_data(engine, mitm_data)
    if autoclose:
        engine.dispose()
    return engine
