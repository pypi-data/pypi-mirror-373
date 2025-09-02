from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Iterator
from typing import TYPE_CHECKING, Self

import pandas as pd
import pydantic
from pydantic import ConfigDict

from mitm_tooling.definition import get_mitm_def
from mitm_tooling.definition.definition_representation import MITM, ConceptName
from mitm_tooling.utilities.python_utils import take_first

from ..common import MITMTypeError
from .header import Header, HeaderEntry

if TYPE_CHECKING:
    from .mitm_data import MITMData


class StreamingConceptData(pydantic.BaseModel):
    """
    This model represents streamable data for a specific concept, including its DataFrame structure (empty df with just column names) and a list of iterators for chunks of instances.

    The instance chunks are expected to be tuples of `(DataFrame, list[HeaderEntry])` where the DataFrame contains the actual data and the list of `HeaderEntry` provides metadata about the occurring types.

    The outer list of iterators allows for multiple streams of data for the same concept, particularly when constructing the stream ad-hoc without prior knowledge of the contained concepts, e.g., when adding types individually and out-of-order w.r.t. concepts.

    Note: Streamed data is assumed to be readable once.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    structure_df: pd.DataFrame
    chunk_iterators: list[Iterator[tuple[pd.DataFrame, list[HeaderEntry]]]] = pydantic.Field(default_factory=list)


class StreamingMITMData(Iterable[tuple[ConceptName, StreamingConceptData]], pydantic.BaseModel):
    """
    This model represents streamable MITM data as a collection of `StreamingConceptData`.

    By default, it is assumed that the streams are in the "generalized" form, meaning that the keys of the dictionary correspond to main concepts.

    Note: Streamed data is assumed to be readable once.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    mitm: MITM
    data_sources: dict[ConceptName, StreamingConceptData] = pydantic.Field(default_factory=dict)

    def __iter__(self):
        return iter(self.data_sources.items())

    def as_generalized(self) -> Self:
        mitm_def = get_mitm_def(self.mitm)
        combined_data_sources = defaultdict(list)
        for c, ds in self:
            combined_data_sources[mitm_def.get_parent(c)].append(ds)
        data_sources = {}
        for c, ds_list in combined_data_sources.items():
            structure_dfs = [ds.structure_df for ds in ds_list]
            if not all(a.equals(b) for a, b in zip(structure_dfs[:-1], structure_dfs[1:], strict=False)):
                raise MITMTypeError(f'Concept {c} not generalizable in {self} (structure_dfs differ)')

            data_sources[c] = StreamingConceptData(
                structure_df=take_first(structure_dfs),
                chunk_iterators=[it for ds in ds_list for it in ds.chunk_iterators],
            )
        return StreamingMITMData(mitm=self.mitm, data_sources=data_sources)

    def collect(self) -> MITMData:
        from .mitm_data import MITMData

        hes = []
        concept_dfs = {}
        for c, concept_data in self.as_generalized():
            dfs = [concept_data.structure_df]
            for df_chunks in concept_data.chunk_iterators:
                for df_chunk, hes_ in df_chunks:
                    # df_chunk = df_chunk.reindex(columns=concept_data.structure_df.columns)
                    dfs.append(df_chunk)
                    hes.extend(hes_)
            concept_dfs[c] = pd.concat(dfs, axis='index', ignore_index=True)

        header = Header.of(self.mitm, *hes)
        return MITMData(header=header, concept_dfs=concept_dfs)
