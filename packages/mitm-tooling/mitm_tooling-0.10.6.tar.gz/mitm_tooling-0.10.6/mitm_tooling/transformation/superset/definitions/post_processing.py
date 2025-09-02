from typing import Literal

import pydantic

from .core import ColumnName, FrozenSupersetDefinition, SupersetPostProcessing


class PivotOperator(FrozenSupersetDefinition):
    operator: str = 'mean'


class PivotOptions(FrozenSupersetDefinition):
    aggregates: list[dict[ColumnName, PivotOperator]]
    columns: list[ColumnName] = pydantic.Field(default_factory=list)
    index: list[ColumnName] = pydantic.Field(default_factory=list)
    drop_missing_columns: bool = False


class Pivot(SupersetPostProcessing):
    operation: Literal['pivot'] = 'pivot'

    options: PivotOptions


class RenameOptions(FrozenSupersetDefinition):
    columns: dict[ColumnName, ColumnName | None] = pydantic.Field(default_factory=dict)
    level: int = 0
    inplace: bool | None = True


class Rename(SupersetPostProcessing):
    operation: Literal['rename'] = 'rename'
    options: RenameOptions


class Flatten(SupersetPostProcessing):
    operation: Literal['flatten'] = 'flatten'
