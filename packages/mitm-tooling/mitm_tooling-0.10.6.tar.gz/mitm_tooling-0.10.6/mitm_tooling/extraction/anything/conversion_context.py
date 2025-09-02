import contextlib
import os.path
import re
import tempfile
from collections.abc import Callable, Generator
from typing import Literal

import pandas as pd
import sqlalchemy as sa
from pydantic import AnyUrl

from mitm_tooling.definition import MITM, get_mitm_def, mitm_definitions
from mitm_tooling.representation.sql import TableName
from mitm_tooling.utilities.io_utils import (
    FilePath,
    dump_pydantic_to_str,
    dump_serialized_to_str,
    ensure_directory_exists,
    ensure_ext,
    load_pydantic,
    use_string_io,
)
from mitm_tooling.utilities.sql_utils import create_sa_engine

from ..relational.data_models import DBProbe
from ..relational.data_models.db_meta import DBMetaInfoBase
from ..relational.data_models.db_probe import DBProbeMinimal
from ..relational.mapping import BoundExportable, StandaloneDBMapping


def in_memory_sqlite_engine() -> sa.Engine:
    return create_sa_engine(AnyUrl('sqlite://'), poolclass=sa.StaticPool)


def file_path_sqlite_engine(fp: FilePath) -> sa.Engine:
    return create_sa_engine(AnyUrl(f'sqlite:///{fp}'), poolclass=sa.StaticPool)


def external_engine(url: str | AnyUrl) -> sa.Engine:
    url = AnyUrl(url) if isinstance(url, str) else url
    return create_sa_engine(url, poolclass=sa.StaticPool)


@contextlib.contextmanager
def in_memory_sqlite_ctxt() -> Generator[sa.Engine, None, None]:
    e = in_memory_sqlite_engine()
    yield e
    e.dispose()


@contextlib.contextmanager
def tempdir_sqlite_ctxt() -> Generator[sa.Engine, None, None]:
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True, delete=True) as td:
        fp = os.path.join(td, 'temp.sqlite')
        e = file_path_sqlite_engine(fp)
        yield e
        e.dispose()


@contextlib.contextmanager
def external_sql_ctxt(url: str | AnyUrl) -> Generator[sa.Engine, None, None]:
    e = external_engine(url)
    yield e
    e.dispose()


def _sanitize_table_name(name: str) -> str:
    """
    Sanitize a string to be a valid SQLite table name:
    - Replace invalid characters with underscores
    - Ensure starts with a letter or underscore
    """
    safe = re.sub(r'[^0-9a-zA-Z_]', '_', name)
    if not re.match(r'^[a-zA-Z_]', safe):
        safe = f't_{safe}'
    return safe


def dump_dfs_into_sqlite(
    df_loaders: dict[str, Callable[[], pd.DataFrame]], engine: sa.Engine | None = None
) -> tuple[sa.Engine, list[tuple[TableName, int]]]:
    """
    Dump data frames `dfs` into an SQLite database.
    The key is used as the table name.

    :param df_loaders: a mapping of table names to callables that return `DataFrames`
    :param engine: the target SQlAlchemy `Engine`, defaults to in-memory SQLite
    :return: the engine that was inserted into and some information about the inserted tables
    """

    engine = engine or in_memory_sqlite_engine()

    insertions = []
    for name, df_loader in df_loaders.items():
        table_name = _sanitize_table_name(name)
        df = df_loader()
        rows = df.to_sql(
            name=table_name,
            con=engine,
            if_exists='replace',  # overwrite existing tables of the same name
            index=False,
            method='multi',  # efficient batching for SQLite
            chunksize=10_000,
        )
        insertions.append((table_name, rows))
    return engine, insertions


def probe_engine(engine: sa.Engine, sample_size=100) -> DBProbe:
    from mitm_tooling.extraction.relational.data_models import DBMetaInfo
    from mitm_tooling.extraction.relational.db import sa_reflect

    sa_meta, a_m = sa_reflect(engine)
    db_meta = DBMetaInfo.from_sa_meta(sa_meta, default_schema=a_m.default_schema)
    from sqlalchemy.orm.session import Session

    with Session(engine) as session:
        from mitm_tooling.extraction.relational.db import create_db_probe

        return create_db_probe(session, db_meta, sample_size=sample_size)


def mk_file_loaders(files: list[FilePath], **kwargs) -> dict[str, Callable[[], pd.DataFrame]]:
    def tbl_name(p: FilePath) -> str:
        return os.path.splitext(os.path.split(p)[1])[0]

    def df_loader(p: FilePath) -> Callable[[], pd.DataFrame]:
        return lambda: pd.read_csv(p, **kwargs)

    return {tbl_name(p): df_loader(p) for p in files}


def load_db_mapping(
    db_mapping_path: FilePath, subpath: tuple[str, ...] | None = None, throw: bool = False
) -> StandaloneDBMapping | None:
    return load_pydantic(StandaloneDBMapping, db_mapping_path, subpath=subpath, throw=throw)


def save_text_files(folder_path: FilePath, files: dict[str, str]):
    folder = ensure_ext(folder_path, '/', override_ext=True)
    ensure_directory_exists(folder)
    for fn, contents in files.items():
        with use_string_io(
            os.path.join(folder, fn), expected_file_ext='.txt', mode='w', create_file_if_necessary=True
        ) as f:
            f.write(contents)
    with use_string_io(
        os.path.join(folder, 'all.txt'), expected_file_ext='.txt', mode='w', create_file_if_necessary=True
    ) as f:
        for fn, contents in files.items():
            f.write(f'=== {fn} ===\n')
            f.write(contents)
            f.write('\n')


def mk_llm_context_bundle(mitm: MITM, db_probe: DBProbe) -> dict[str, str]:
    dbm_ = DBMetaInfoBase(db_structure=db_probe.db_meta.db_structure)
    dbp_ = DBProbeMinimal(db_table_probes=db_probe.db_table_probes)
    a = dump_pydantic_to_str(dbm_, serialize_as_any=False)
    b = dump_pydantic_to_str(dbp_, serialize_as_any=False)
    db_info = a + '\n' + b
    print(mitm)
    mitm_def = get_mitm_def(mitm)
    print(mitm_definitions)
    mitm_definition = dump_pydantic_to_str(mitm_def)
    db_mapping_schema = dump_serialized_to_str(StandaloneDBMapping.model_json_schema(by_alias=True))
    instructions = """
You are provided with the database schema and some sample data from a SQL database.
This is in `db_info.txt`.
Next, consider the json schema for a `StandaloneDBMapping` in `db_mapping_schema.yaml`.
It describes the structure of a `StandaloneDBMapping` and the types of its components.
Finally, consider `mitm_def.yaml`, which contains the definition of a conceptual metamodel.
Please construct a sensible `StandaloneDBMapping` that maps (some of) the tables in the database to concepts present in the MITM definition.
Provide the mapping in yaml format such that it conforms to the provided schema (`db_mapping_schema.yaml`).

You can create any SQL transformations you need to do before the mapping by using the `VirtualViewCreation` in the `StandaloneDBMapping`.
The virtual views can be referenced by the `SourceDBType` virtual.
Remember that you can also simply use raw SQL queries via a `RawCompiled` `TableCreation` in the `VirtualDBCreation`. 

You do not have to map all tables in the database; just whatever is sensible.
Chat with the user to determine what to do if you are unsure.
"""
    return {
        'instructions.txt': instructions,
        'db_info.txt': db_info,
        'db_mapping_schema.yaml': db_mapping_schema,
        'mitm_def.yaml': mitm_definition,
    }


class ConvContext:
    """
    A basic conversion context.
    It supports conversion operations on the bound `Engine`.
    """

    def __init__(self, engine: sa.Engine):
        self.engine = engine

    def apply_db_mapping(self, db_mapping: StandaloneDBMapping) -> BoundExportable:
        """
        Apply a `StandaloneDBMapping` to the bound `Engine`, returning a `BoundExportable`.
        It can be used to initiate a (streamed) export.

        See `Exportable`.

        :param db_mapping: the `StandaloneDBMapping` to apply
        :return:
        """
        exp = db_mapping.to_exportable(self.engine)
        return exp.bind(self.engine)

    def probe(self) -> DBProbe:
        """
        Probe the database using the bound `Engine`.
        It contains information about the database schema and some sample-based inference of column types and value summaries.

        See `DBProbe`.

        :return: the probe result
        """
        return probe_engine(self.engine)

    def gen_llm_context(self, mitm: MITM, folder_path: FilePath | None = None) -> dict[str, str]:
        """
        Generate, and optionally save, some textual context for an LLM to use for suggesting a `StandaloneDBMapping`.

        :param mitm: the target MITM
        :param folder_path: optionally, a folder to save the context files to
        :return: a dictionary mapping file names to file contents
        """
        db_probe = self.probe()
        bundle = mk_llm_context_bundle(mitm, db_probe)
        if folder_path is not None:
            save_text_files(folder_path, bundle)
        return bundle


class MutatingConvContext(ConvContext):
    """
    A conversion context that allows mutating operations, e.g., importing `DataFrames` into the database.
    See `ConvContext`.
    """

    def __init__(self, engine: sa.Engine):
        super().__init__(engine)

    def add_dfs(self, df_loaders: dict[str, Callable[[], pd.DataFrame]]) -> list[tuple[TableName, int]]:
        """
        Insert the `DataFrames` provided by the `df_loaders` into the database using the bound `Engine`.

        :param df_loaders: a mapping of table names to callables that return `DataFrames`
        :return: some information about the inserted tables
        """

        _, insertions = dump_dfs_into_sqlite(df_loaders, engine=self.engine)
        return insertions


@contextlib.contextmanager
def sqlite_ctxt(variant: Literal['memory', 'tempdir'] = 'memory') -> Generator[sa.Engine, None, None]:
    ctxt_mngr = in_memory_sqlite_ctxt if variant == 'memory' else tempdir_sqlite_ctxt
    with ctxt_mngr() as engine:
        yield engine


@contextlib.contextmanager
def local_conv_ctxt(variant: Literal['memory', 'tempdir'] = 'memory') -> Generator[MutatingConvContext, None, None]:
    """
    A conversion context that uses a transient local SQLAlchemy engine.
    Can be either in-memory or on disk (in a temporary directory).

    :param variant: the variant of the local SQLite DB to use, either 'memory' or 'tempdir'
    :return:
    """
    with sqlite_ctxt(variant) as engine:
        yield MutatingConvContext(engine)


@contextlib.contextmanager
def external_conv_ctxt(sql_alchemy_url: str | AnyUrl) -> Generator[ConvContext, None, None]:
    """
    A conversion context that uses an external SQLAlchemy engine.
    It does not support mutating operations (e.g., adding `DataFrames`).

    :param sql_alchemy_url: the SQLAlchemy connection URL of the external database
    :return:
    """
    with external_sql_ctxt(sql_alchemy_url) as engine:
        yield ConvContext(engine)
