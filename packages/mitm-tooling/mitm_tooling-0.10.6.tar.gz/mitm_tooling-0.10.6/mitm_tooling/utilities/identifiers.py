import uuid
from uuid import UUID

import pydantic


def mk_uuid() -> pydantic.UUID4:
    return uuid.uuid4()


def mk_short_uuid_str(existing_uuid: uuid.UUID | None = None) -> str:
    return (existing_uuid or mk_uuid()).hex[:12]


def name_plus_uuid(name: str, uuid: UUID | None = None, sep: str = '-') -> str:
    return f'{name}{sep}{mk_short_uuid_str(uuid)}'


def naive_pluralize(name: str) -> str:
    return f'{name}s'
