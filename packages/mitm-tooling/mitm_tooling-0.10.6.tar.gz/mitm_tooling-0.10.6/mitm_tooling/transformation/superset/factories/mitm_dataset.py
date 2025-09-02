from collections.abc import Iterable, Sequence
from typing import Literal
from uuid import UUID

from mitm_tooling.definition import MITM
from mitm_tooling.representation.intermediate import Header
from mitm_tooling.utilities.identifiers import mk_uuid, name_plus_uuid

from ..definitions import RelatedDashboard, RelatedSlice, RelatedTable, SupersetMitMDatasetDef


def mk_related_obj(
    kind: Literal['table', 'slice', 'dashboard'], uuid: UUID
) -> RelatedTable | RelatedSlice | RelatedDashboard | None:
    match kind:
        case 'table':
            return RelatedTable(uuid=uuid)
        case 'slice':
            return RelatedSlice(uuid=uuid)
        case 'dashboard':
            return RelatedDashboard(uuid=uuid)


def mk_related_objs(
    kind: Literal['table', 'slice', 'dashboard'], uuids: Iterable[UUID]
) -> Iterable[RelatedTable] | Iterable[RelatedSlice] | Iterable[RelatedDashboard] | None:
    if uuids:
        return [mk_related_obj(kind, uuid) for uuid in uuids]


def mk_mitm_dataset(
    name: str,
    mitm: MITM,
    database_uuid: UUID,
    header: Header | None = None,
    table_uuids: list[UUID] | None = None,
    slice_uuids: Sequence[UUID] | None = None,
    dashboard_uuids: Sequence[UUID] | None = None,
    uuid: UUID | None = None,
    uniquify_name: bool = False,
) -> SupersetMitMDatasetDef:
    uuid = uuid or mk_uuid()
    if uniquify_name:
        name = name_plus_uuid(name, uuid)
    return SupersetMitMDatasetDef(
        dataset_name=name,
        mitm=mitm,
        mitm_header=header,
        uuid=uuid or mk_uuid(),
        database_uuid=database_uuid,
        tables=mk_related_objs('table', table_uuids),
        slices=mk_related_objs('slice', slice_uuids),
        dashboards=mk_related_objs('dashboard', dashboard_uuids),
    )
