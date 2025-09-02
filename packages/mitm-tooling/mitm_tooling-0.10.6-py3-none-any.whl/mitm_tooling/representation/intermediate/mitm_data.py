from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from typing import TYPE_CHECKING, Self

import pandas as pd
import pydantic
from pydantic import ConfigDict

from mitm_tooling.definition import get_mitm_def
from mitm_tooling.definition.definition_representation import ConceptName
from mitm_tooling.utilities.df_utils import chunk_df

from ..common import MITMTypeError, mk_concept_file_header
from .header import Header

if TYPE_CHECKING:
    from .streaming_mitm_data import StreamingMITMData


class MITMData(Iterable[tuple[ConceptName, pd.DataFrame]], pydantic.BaseModel):
    """
    This model represents MITM data in a semi-compacted form; essentially the proposed csv file format.
    The individual DataFrames are expected to have fixed columns, corresponding to the type information in the `header`.
    In particular, each DataFrame should have the static columns as defined the `concept` it belongs to,
    and additionally a variable number of attribute columns named `a_1,a_2,...`.

    By default, it is assumed that the DataFrames are in the "generalized" form, meaning that the keys of the dictionary correspond to main concepts.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    header: Header
    concept_dfs: dict[ConceptName, pd.DataFrame] = pydantic.Field(default_factory=dict)

    def __iter__(self):
        return iter(self.concept_dfs.items())

    def as_generalized(self) -> Self:
        """
        Generalizes the MITMData by concatenating all DataFrames with the same _parent_ concept.
        For example, for a concept hierarchy like:

        - observation
            - measurement
            - event

        The DataFrames for `measurement` and `event` will be concatenated into the DataFrame for `observation`.
        """
        mitm_def = get_mitm_def(self.header.mitm)
        dfs = defaultdict(list)
        for c, df in self.concept_dfs.items():
            c_ = mitm_def.get_parent(c)
            if not c_:
                raise MITMTypeError(f'Encountered unknown concept key: "{c}".')
            dfs[c_].append(df)
        dfs = {c: pd.concat(dfs_, axis='index', ignore_index=True) for c, dfs_ in dfs.items()}
        return MITMData(header=self.header, concept_dfs=dfs)

    def as_specialized(self) -> Self:
        """
        Specializes the MITMData by splitting all DataFrames into their leaf concepts.
        For example, for a concept hierarchy like:

        - observation
            - measurement
            - event

        The DataFrame for `observation` will be split into `measurement` and `event`.
        """
        mitm_def = get_mitm_def(self.header.mitm)
        dfs = {}
        for c, df in self:
            if mitm_def.get_properties(c).is_abstract:
                # leaf_concepts = mitm_def.get_leafs(c)

                for sub_c_key, idx in df.groupby('kind').groups.items():
                    try:
                        sub_c = mitm_def.inverse_concept_key_map[str(sub_c_key)]
                    except KeyError:
                        raise MITMTypeError(f'Encountered unknown sub concept key: "{sub_c_key}".') from None
                    dfs[sub_c] = df.loc[idx]
            else:
                dfs[c] = df
        return MITMData(header=self.header, concept_dfs=dfs)

    def as_streaming(self, chunk_size: int | None = 100_000) -> StreamingMITMData:
        from .streaming_mitm_data import StreamingConceptData, StreamingMITMData

        h = self.header
        mitm = h.mitm
        generalized_dict = h.as_generalized_dict
        mitm_def = get_mitm_def(mitm)
        max_ks = {c: max((he.attr_k for he in t_hes.values()), default=0) for c, t_hes in generalized_dict.items()}

        data_sources = {}
        for c, df in self.as_generalized():
            structure_df = pd.DataFrame(columns=mk_concept_file_header(mitm, c, max_ks[c])[0])

            props = mitm_def.get_properties(c)
            typing_col = props.typing_concept
            he_map = generalized_dict[c]

            def local_iter(df=df, he_map=he_map, typing_col=typing_col):
                dfs = chunk_df(df, chunk_size=chunk_size)
                for df_chunk in dfs:
                    included_types = df_chunk[typing_col].unique()
                    yield df_chunk, [he_map[str(type_name)] for type_name in included_types]

            if props.is_abstract:
                chunk_iterators = [local_iter(df=df.loc[idx]) for idx in df.groupby('kind').groups.values()]
            else:
                chunk_iterators = [local_iter()]

            data_sources[c] = StreamingConceptData(structure_df=structure_df, chunk_iterators=chunk_iterators)

        return StreamingMITMData(mitm=mitm, data_sources=data_sources)
