from typing import Any

import pydantic

from mitm_tooling.utilities.identifiers import name_plus_uuid

from .constants import StrUUID, SupersetDefFile
from .core import SupersetColumn, SupersetMetric
from .identifiers import DatasetIdentifier


class SupersetDatasetDef(SupersetDefFile):
    table_name: str
    schema_name: str = pydantic.Field(alias='schema')
    uuid: StrUUID
    database_uuid: StrUUID
    main_dttm_col: str | None = None
    description: str | None = None
    default_endpoint: str | None = None
    offset: int = 0
    cache_timeout: str | None = None
    catalog: str | None = None
    sql: str | None = None
    params: Any = None
    template_params: Any = None
    is_managed_externally: bool = True
    external_url: str | None = None
    filter_select_enabled: bool = True
    fetch_values_predicate: str | None = None
    extra: dict[str, Any] = pydantic.Field(default_factory=dict)
    normalize_columns: bool = False
    always_filter_main_dttm: bool = False
    metrics: list[SupersetMetric] = pydantic.Field(default_factory=list)
    columns: list[SupersetColumn] = pydantic.Field(default_factory=list)
    version: str = '1.0.0'

    @property
    def filename(self):
        return name_plus_uuid(self.table_name, self.uuid, sep='_')

    @property
    def identifier(self) -> DatasetIdentifier:
        return DatasetIdentifier(uuid=self.uuid, table_name=self.table_name, id=-1)
