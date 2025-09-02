from collections.abc import Iterable

import pandas as pd

from mitm_tooling.definition import ConceptName, TypeName

from ..intermediate.header import HeaderEntry

"""
A stream of MITM data frames, where the data is grouped by concept and type.
In contrast to `StreamingMITMDataFrames`, the type information (`Header`) is not known in advance.
"""
MITMDataFrameStream = Iterable[tuple[ConceptName, Iterable[tuple[TypeName, Iterable[pd.DataFrame]]]]]
"""
A stream of MITM data frames, where the data is grouped by concept and type, and includes type information (e.g., attributes/columns) next to the data frames.
In contrast to `StreamingMITMDataFrames`, the type information (`Header`) is not known in advance.
"""
TypedMITMDataFrameStream = Iterable[tuple[ConceptName, Iterable[tuple[TypeName, HeaderEntry, Iterable[pd.DataFrame]]]]]
