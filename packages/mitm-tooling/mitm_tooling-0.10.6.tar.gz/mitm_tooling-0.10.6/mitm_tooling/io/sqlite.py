import logging
from typing import Self

import sqlalchemy as sa
from pydantic import AnyUrl

from mitm_tooling.representation.intermediate import Header, MITMData, StreamingMITMData
from mitm_tooling.representation.sql import mk_sql_rep_schema
from mitm_tooling.utilities.io_utils import DataSink, DataSource, FilePath, ensure_directory_exists
from mitm_tooling.utilities.sql_utils import AnyDBBind, create_sa_engine

from ..definition import MITM
from ..extraction.relational.mapping import BoundExportable, Exportable
from ..representation.df import MITMDataFrames
from ..transformation.sql import insert_exportable, insert_mitm_data, insert_mitm_dataframes
from .common import MITMExport, MITMIOError, StreamingMITMImport, ensure_filepath

logger = logging.getLogger(__name__)


def infer_mitm_from_sqlite(p: FilePath) -> MITM | None:
    try:
        return SQLiteImport.read_mitm(p)
    except MITMIOError:
        return None


class SQLiteImport(StreamingMITMImport):
    """
    Import of the specific SQLite file format designed for MITMs.
    """

    @classmethod
    def read_mitm(cls, source: DataSource):
        return cls._read_header(source).mitm

    @classmethod
    def _read_header(cls, source: DataSource, **kwargs) -> Header:
        ensure_filepath(source)

        try:
            from mitm_tooling.transformation.sql import mitm_db_into_header

            eng = create_sa_engine(AnyUrl(f'sqlite:///{source}'), poolclass=sa.StaticPool)
            return mitm_db_into_header(eng)
        except Exception as e:
            raise MITMIOError(f'Error reading MITM Header from SQLite: {source}') from e

    @classmethod
    def _read_streaming(cls, source: DataSource, **kwargs) -> StreamingMITMData:
        ensure_filepath(source)

        try:
            from mitm_tooling.transformation.sql import mitm_db_into_header, sql_rep_into_exportable

            eng = create_sa_engine(AnyUrl(f'sqlite:///{source}'), poolclass=sa.StaticPool)
            h = mitm_db_into_header(eng)
            sql_rep_schema = mk_sql_rep_schema(h)
            exp = sql_rep_into_exportable(h, sql_rep_schema)
            return exp.generate_streaming_mitm_data(eng)
        except Exception as e:
            raise MITMIOError(f'Error reading MITMData (streamed) from SQLite: {source}') from e

    @classmethod
    def _read(cls, source: DataSource, **kwargs) -> MITMData:
        ensure_filepath(source)

        try:
            from mitm_tooling.transformation.sql import mitm_db_into_header, sql_rep_into_exportable

            eng = create_sa_engine(AnyUrl(f'sqlite:///{source}'), poolclass=sa.StaticPool)
            h = mitm_db_into_header(eng)
            sql_rep_schema = mk_sql_rep_schema(h)
            exp = sql_rep_into_exportable(h, sql_rep_schema)
            return exp.generate_mitm_data(eng)
        except Exception as e:
            raise MITMIOError(f'Error reading MITMData from SQLite: {source}') from e

    def read_header(self, source: DataSource, **kwargs) -> Header:
        return self._read_header(source, **kwargs)

    def read_streaming(self, source: DataSource, **kwargs) -> StreamingMITMData:
        return self._read_streaming(source, **kwargs)

    def read(self, source: DataSource, **kwargs) -> MITMData:
        return self._read(source, **kwargs)


class SQLiteExport(MITMExport):
    """
    Export `MITMData` to the specific SQlite file format designed for MITMs.
    """

    mitm_data: MITMData

    def write(self, sink: DataSink, **kwargs) -> None:
        ensure_filepath(sink, test_existence=False)
        ensure_directory_exists(sink)
        try:
            engine = create_sa_engine(AnyUrl(f'sqlite:///{str(sink)}'), poolclass=sa.StaticPool)
            insert_mitm_data(engine, self.mitm_data)
        except Exception as e:
            raise MITMIOError(f'Error exporting MITMData to SQLite: {sink}') from e
        return None


class ExportableSQLiteExport(MITMExport):
    """
    Export a `BoundExportable` to the specific SQLite file format designed for MITMs.
    """

    bound_exportable: BoundExportable

    @classmethod
    def from_exportable(cls, exportable: Exportable, bind: AnyDBBind) -> Self:
        return cls(
            mitm=exportable.mitm,
            bound_exportable=exportable.bind(bind),
            filename=exportable.filename or f'{exportable.mitm}.zip',
        )

    def write(self, sink: DataSink, stream_data: bool = False, **kwargs) -> None:
        ensure_filepath(sink, test_existence=False)
        ensure_directory_exists(sink)

        try:
            target = create_sa_engine(AnyUrl(f'sqlite:///{str(sink)}'), poolclass=sa.StaticPool)
            insert_exportable(
                target, self.bound_exportable.bind, self.bound_exportable.exportable, stream_data=stream_data
            )
        except Exception as e:
            raise MITMIOError(f'Error exporting Exportable to SQLite: {sink}') from e
        return None


class MITMDataFramesSQLiteExport(MITMExport):
    """
    Directly export `MITMDataFrames` to the specific SQLite file format designed for MITMs.
    """

    mitm_dataframes: MITMDataFrames

    def write(self, sink: DataSink, **kwargs) -> None:
        ensure_filepath(sink, test_existence=False)
        ensure_directory_exists(sink)

        try:
            target = create_sa_engine(AnyUrl(f'sqlite:///{str(sink)}'), poolclass=sa.StaticPool)
            insert_mitm_dataframes(target, self.mitm_dataframes)
        except Exception as e:
            raise MITMIOError(f'Error exporting MITMDataFrames to SQLite: {sink}') from e
        return None
