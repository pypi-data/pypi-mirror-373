from collections.abc import Iterable, Iterator

import pandas as pd

from mitm_tooling.definition import TypeName, get_mitm_def
from mitm_tooling.extraction.relational.mapping import Exportable
from mitm_tooling.representation.common import MITMTypeError
from mitm_tooling.representation.df import (
    MITMDataFrames,
    MITMDataFrameStream,
    StreamingMITMDataFrames,
    TypedMITMDataFrameStream,
    collect_typed_mitm_dataframe_stream,
)
from mitm_tooling.representation.intermediate import HeaderEntry
from mitm_tooling.utilities.sql_utils import AnyDBBind, use_db_bind


def exportable_to_mitm_dataframes_stream(
    source: AnyDBBind,
    exportable: Exportable,
    stream_data: bool = False,
) -> MITMDataFrameStream:
    """
    Apply the `Exportable` to the `source` database to generate a structured stream of data frames.

    See also: `StreamingMITMDataFrames`.

    :param source: a bind to the database to query from
    :param exportable: the `Exportable` to apply
    :param stream_data: whether to query the database in chunks or not
    :return: a `MITMDataFrameStream`
    """

    mitm_def = get_mitm_def(exportable.mitm)
    with use_db_bind(source) as source_conn:
        for c, dps in exportable.data_providers.items():

            def df_chunks_iter(c=c, dps=dps) -> Iterator[tuple[TypeName, Iterable[pd.DataFrame]]]:
                for dp in dps:
                    chunks = (
                        dp.instance_provider.apply_db_chunked(source_conn)
                        if stream_data
                        else [dp.instance_provider.apply_db(source_conn)]
                    )
                    for df_chunk in chunks:
                        df_chunk = dp.instance_postprocessor.apply_df(df_chunk)
                        for type_name, type_idx in df_chunk.groupby(
                            mitm_def.get_properties(c).typing_concept
                        ).groups.items():
                            hes = dp.header_entry_provider.apply_df(df_chunk.loc[type_idx])  # noqa
                            if not len(hes) == 1:
                                raise MITMTypeError(f'Expected exactly one header entry per type, got {len(hes)}.')
                            he = hes[0]
                            typed_df = df_chunk.loc[type_idx].rename(columns=he.attr_name_map)
                            yield str(type_name), (typed_df,)

            yield c, df_chunks_iter(c, dps)


def exportable_to_typed_mitm_dataframes_stream(
    source: AnyDBBind,
    exportable: Exportable,
    stream_data: bool = False,
) -> TypedMITMDataFrameStream:
    """
    Apply the `Exportable` to the `source` database to generate a structured stream of data frames that includes explicit type information.

    See also: `StreamingMITMDataFrames`.

    :param source: a bind to the database to query from
    :param exportable: the `Exportable` to apply
    :param stream_data: whether to query the database in chunks or not
    :return: a `TypedMITMDataFrameStream`
    """

    mitm_def = get_mitm_def(exportable.mitm)
    with use_db_bind(source) as source_conn:
        for c, dps in exportable.data_providers.items():

            def typed_df_chunks_iter(c=c, dps=dps) -> Iterator[tuple[TypeName, HeaderEntry, Iterable[pd.DataFrame]]]:
                for dp in dps:
                    chunks = (
                        dp.instance_provider.apply_db_chunked(source_conn)
                        if stream_data
                        else [dp.instance_provider.apply_db(source_conn)]
                    )
                    for df_chunk in chunks:
                        df_chunk = dp.instance_postprocessor.apply_df(df_chunk)
                        for type_name, type_idx in df_chunk.groupby(
                            mitm_def.get_properties(c).typing_concept
                        ).groups.items():
                            # exactly one header entry per type
                            hes = dp.header_entry_provider.apply_df(df_chunk.loc[type_idx])  # noqa
                            if not len(hes) == 1:
                                raise MITMTypeError(f'Expected exactly one header entry per type, got {len(hes)}.')
                            he = hes[0]
                            # de-anonymize the columns a_i -> actual attribute name
                            typed_df = df_chunk.loc[type_idx].rename(columns=he.attr_name_map)
                            yield str(type_name), he, (typed_df,)

            yield c, typed_df_chunks_iter(c, dps)


def exportable_to_streaming_mitm_dataframes(
    source: AnyDBBind,
    exportable: Exportable,
    stream_data: bool = False,
) -> StreamingMITMDataFrames:
    header = exportable.generate_header(source)
    df_iters = exportable_to_mitm_dataframes_stream(source, exportable, stream_data=stream_data)
    return StreamingMITMDataFrames(header=header, df_iters=df_iters)


def exportable_to_mitm_dataframes(
    source: AnyDBBind,
    exportable: Exportable,
    stream_data: bool = False,
) -> MITMDataFrames:
    return collect_typed_mitm_dataframe_stream(
        exportable.mitm, exportable_to_typed_mitm_dataframes_stream(source, exportable, stream_data=stream_data)
    )
