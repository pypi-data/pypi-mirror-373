import itertools

import pandas as pd

from mitm_tooling.data_types import convert
from mitm_tooling.definition import ConceptName, TypeName, get_mitm_def
from mitm_tooling.representation import mk_concept_file_header
from mitm_tooling.representation.common import MITMTypeError
from mitm_tooling.representation.df import (
    MITMDataFrames,
    TypedMITMDataFrameStream,
    collect_typed_mitm_dataframe_stream,
)
from mitm_tooling.representation.intermediate import Header, HeaderEntry, MITMData, StreamingMITMData


def unpack_concept_table_as_typed_dfs(
    header: Header, concept: ConceptName, df: pd.DataFrame
) -> dict[TypeName, pd.DataFrame]:
    """
    Unpack a concept table into a dict of typed dataframes.
    The data frame is expected to have columns in the format of `MITMData`, i.e.,
    There are columns for the base columns determined by the concept in the specified MITM,
    and numbered attribute columns with types matching the `HeaderEntries` specified in the header.
    The resulting data frames have the structure of `MITMDataFrames`.

    :param header: the header of the MITM data
    :param concept: the target concept
    :param df: data frame to unpack
    :return: a dict of data frames, keyed by type name
    """

    mitm_def = get_mitm_def(header.mitm)
    concept_properties, concept_relations = mitm_def.get(concept)

    with_header_entry: dict[tuple[str, TypeName], tuple[HeaderEntry, pd.DataFrame]] = {}
    if concept_properties.is_abstract:  # e.g. MAED.observation
        for (key, typ), idx in df.groupby(['kind', concept_properties.typing_concept]).groups.items():
            key, type_name = str(key), str(typ)
            specific_concept = mitm_def.inverse_concept_key_map[key]
            he = header.get(specific_concept, type_name)
            if he is None:
                raise MITMTypeError(f'Missing type entry for {specific_concept}:{type_name} in header.')
            with_header_entry[(specific_concept, type_name)] = (he, df.loc[idx])
    else:
        for typ, idx in df.groupby(concept_properties.typing_concept).groups.items():
            type_name = str(typ)
            he = header.get(concept, type_name)
            if he is None:
                raise MITMTypeError(f'Missing type entry for {concept}:{type_name} in header.')
            with_header_entry[(concept, type_name)] = (he, df.loc[idx])

    res = {}
    for (concept, _type_name), (he, type_df) in with_header_entry.items():
        k = he.attr_k
        normal_form_cols, normal_form_dts = mk_concept_file_header(header.mitm, concept, k)
        type_df = type_df.reindex(columns=normal_form_cols)
        type_df = type_df.rename(columns=he.attr_name_map)
        dt_map = dict(
            itertools.chain(
                ((a, dt) for a, dt in normal_form_dts.items() if a in set(type_df.columns)), he.iter_attr_dtype_pairs()
            )
        )
        res[he.type_name] = convert.convert_df(type_df, dt_map)

    return res


def mitm_data_into_mitm_dataframes(mitm_data: MITMData) -> MITMDataFrames:
    """
    Unpack a `MITMData` object into a `MITMDataFrames` object.
    """
    mitm_data = mitm_data.as_specialized()
    return MITMDataFrames(
        header=mitm_data.header,
        dfs={concept: unpack_concept_table_as_typed_dfs(mitm_data.header, concept, df) for concept, df in mitm_data},
    )


def streaming_mitm_data_into_typed_mitm_dataframe_stream(
    streaming_mitm_data: StreamingMITMData,
) -> TypedMITMDataFrameStream:
    """
    Incrementally unpack `StreamingMITMData` into a `TypedMITMDataFrameStream`.
    """
    mitm = streaming_mitm_data.mitm

    def itr():
        for _, streaming_concept in streaming_mitm_data.data_sources.items():
            for iters in streaming_concept.chunk_iterators:
                for df, hes in iters:
                    if len(hes) > 0:
                        shared_concept = hes[0].concept
                        for he in hes[1:]:
                            if shared_concept != he.concept:
                                raise MITMTypeError('Inhomogeneous header entries')
                        h = Header.of(mitm, *hes)

                        def local_iter(df=df, h=h, shared_concept=shared_concept):
                            type_hes = h.as_dict[shared_concept]
                            unpacked = unpack_concept_table_as_typed_dfs(h, shared_concept, df)
                            for type_name, typed_df in unpacked.items():
                                yield type_name, type_hes[type_name], (typed_df,)

                        yield shared_concept, local_iter()

    return itr()


def streaming_mitm_data_into_mitm_dataframes(streaming_mitm_data: StreamingMITMData) -> MITMDataFrames:
    return collect_typed_mitm_dataframe_stream(
        streaming_mitm_data.mitm, streaming_mitm_data_into_typed_mitm_dataframe_stream(streaming_mitm_data)
    )
