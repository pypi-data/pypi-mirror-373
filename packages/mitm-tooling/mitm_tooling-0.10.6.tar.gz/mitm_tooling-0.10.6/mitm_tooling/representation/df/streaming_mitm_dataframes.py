from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

import pandas as pd
import pydantic
from pydantic import ConfigDict

from mitm_tooling.definition import MITM, ConceptName, TypeName

from ..common import MITMSyntacticError
from ..intermediate.header import Header
from .common import MITMDataFrameStream, TypedMITMDataFrameStream

if TYPE_CHECKING:
    from .mitm_dataframes import MITMDataFrames


class StreamingMITMDataFrames(Iterable[tuple[ConceptName, dict[TypeName, pd.DataFrame]]], pydantic.BaseModel):
    """
    This model explicitly represents a stream of structured MITM Data via a collection of Iterables.
    In contrast to the bare `MITMDataFrameStream`, only the instances are (potentially) streamed, not the type information.

    Note: Streamed data is assumed to be readable once.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    header: Header
    df_iters: dict[ConceptName, dict[TypeName, Iterable[pd.DataFrame]]]

    def __iter__(self):
        return iter(self.df_iters.items())

    def stream(self) -> MITMDataFrameStream:
        return ((c, ((t, df_iter) for t, df_iter in dfs.items())) for c, dfs in self.df_iters.items())

    def typed_stream(self) -> TypedMITMDataFrameStream:
        he_dict = self.header.as_dict
        return ((c, ((t, he_dict[c][t], df_iter) for t, df_iter in dfs.items())) for c, dfs in self.df_iters.items())

    def collect(self) -> MITMDataFrames:
        return collect_typed_mitm_dataframe_stream(self.header.mitm, self.typed_stream())


def collect_typed_mitm_dataframe_stream(
    mitm: MITM, typed_mitm_dataframe_stream: TypedMITMDataFrameStream
) -> MITMDataFrames:
    hes = []
    dfs = {}
    for c, tps in typed_mitm_dataframe_stream:
        if c not in dfs:
            dfs[c] = {}
        for t, he, df_iter in tps:
            hes.append(he)
            type_df = pd.concat(df_iter, axis='index', ignore_index=True)
            dfs[c][t] = type_df
    if len(hes) == 0:
        raise MITMSyntacticError('Empty MITMDataFrameStream cannot be converted to MITMDataFrames.')
    header = Header.of(mitm, *hes)
    from .mitm_dataframes import MITMDataFrames

    return MITMDataFrames(header=header, dfs=dfs)
