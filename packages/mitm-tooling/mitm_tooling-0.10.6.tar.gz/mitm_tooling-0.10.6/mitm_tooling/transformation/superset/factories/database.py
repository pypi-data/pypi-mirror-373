from uuid import UUID

from pydantic import AnyUrl

from mitm_tooling.utilities.identifiers import mk_uuid, name_plus_uuid

from ..definitions import SupersetDatabaseDef


def mk_database(
    name: str, sqlalchemy_uri: AnyUrl, uuid: UUID | None = None, uniquify_name: bool = False
) -> SupersetDatabaseDef:
    uuid = uuid or mk_uuid()
    if uniquify_name:
        name = name_plus_uuid(name, uuid)
    return SupersetDatabaseDef(database_name=name, sqlalchemy_uri=sqlalchemy_uri, uuid=uuid)
