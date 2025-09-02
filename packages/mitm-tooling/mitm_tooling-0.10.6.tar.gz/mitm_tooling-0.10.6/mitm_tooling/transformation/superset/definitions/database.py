from typing import Any

import pydantic

from mitm_tooling.utilities.identifiers import name_plus_uuid

from .constants import StrUrl, StrUUID, SupersetDefFile
from .core import SupersetObjectMixin
from .identifiers import DatabaseIdentifier


class SupersetDatabaseDef(SupersetObjectMixin, SupersetDefFile):
    database_name: str
    sqlalchemy_uri: StrUrl
    uuid: StrUUID
    # verbose_name : str | None = None
    cache_timeout: str | None = None
    expose_in_sqllab: bool = True
    allow_run_async: bool = True
    allow_ctas: bool = False
    allow_cvas: bool = False
    allow_dml: bool = False
    allow_file_upload: bool = False
    extra: dict[str, Any] = pydantic.Field(default_factory=lambda: {'allows_virtual_table_explore': True})
    impersonate_user: bool = False
    version: str = '1.0.0'
    ssh_tunnel: None = None

    @property
    def filename(self):
        return name_plus_uuid(self.database_name, self.uuid, sep='_')

    @property
    def identifier(self) -> DatabaseIdentifier:
        return DatabaseIdentifier(uuid=self.uuid, database_name=self.database_name, id=-1)
