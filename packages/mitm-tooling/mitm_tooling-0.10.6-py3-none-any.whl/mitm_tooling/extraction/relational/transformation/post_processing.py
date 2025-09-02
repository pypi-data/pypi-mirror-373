import pydantic

from ..data_models.table_identifiers import AnyTableIdentifier
from .db_transformation import TableTransforms


class TablePostProcessing(pydantic.BaseModel):
    target_table: AnyTableIdentifier
    transforms: list[TableTransforms]


class PostProcessing(pydantic.BaseModel):
    table_postprocessing: list[TablePostProcessing]
