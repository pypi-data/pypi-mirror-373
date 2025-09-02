from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

import pandas as pd
import pydantic
from pydantic import ConfigDict

from mitm_tooling.definition import ConceptName, TypeName

from ...utilities.df_utils import chunk_df
from ..intermediate.header import Header

if TYPE_CHECKING:
    from .streaming_mitm_dataframes import StreamingMITMDataFrames


class MITMDataFrames(Iterable[tuple[ConceptName, dict[TypeName, pd.DataFrame]]], pydantic.BaseModel):
    """
    This model represents normalized MITM Data as a collection of pandas DataFrames, hierarchically organized by concept and type.
    It is intended to be used for in-memory representation of normalized MITM Data, e.g., when feeding it into data science packages.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    header: Header
    dfs: dict[ConceptName, dict[TypeName, pd.DataFrame]]

    def __iter__(self):
        return iter(self.dfs.items())

    def as_streaming(self, chunk_size: int | None = 100_000) -> StreamingMITMDataFrames:
        from .streaming_mitm_dataframes import StreamingMITMDataFrames

        return StreamingMITMDataFrames(
            header=self.header,
            df_iters={
                c: {t: chunk_df(df, chunk_size=chunk_size) for t, df in dfs.items()} for c, dfs in self.dfs.items()
            },
        )
