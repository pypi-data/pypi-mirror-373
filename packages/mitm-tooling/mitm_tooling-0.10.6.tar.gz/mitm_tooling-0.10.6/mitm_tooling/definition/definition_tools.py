from collections.abc import Callable, Iterable
from typing import NotRequired, TypedDict

from .definition_representation import ConceptName, MITMDefinition


def _dummy():
    return None


def _dummy_list():
    return []


type Mapper[T] = Callable[[], T | tuple[str, T]]
type MultiMapper[T] = Callable[[], list[T] | Iterable[tuple[str, T]]]


class ColGroupMaps[T](TypedDict, total=False):
    kind: NotRequired[Mapper[T]]
    type: NotRequired[Mapper[T]]
    identity: NotRequired[MultiMapper[T]]
    inline: NotRequired[MultiMapper[T]]
    foreign: NotRequired[MultiMapper[T]]
    attributes: NotRequired[MultiMapper[T]]


def map_col_groups[T](
    mitm_def: MITMDefinition,
    concept: ConceptName,
    col_group_maps: ColGroupMaps[T],
    prepended_cols: MultiMapper | None = None,
    appended_cols: MultiMapper | None = None,
    ensure_unique: bool = True,
) -> tuple[list[T], dict[str, T]]:
    concept_properties = mitm_def.get_properties(concept)

    created_results = {}
    results = []

    def add_results(cols: Iterable[T | tuple[str, T]]):
        for item in cols:
            if isinstance(item, tuple):
                name, result = item
            else:
                result = item
                name = str(item)
            if result is not None and (not ensure_unique or name not in created_results):
                created_results[name] = result
                results.append(result)

    if prepended_cols:
        add_results(prepended_cols())
    for column_group in concept_properties.column_group_ordering:
        match column_group:
            case 'kind' if concept_properties.is_abstract or concept_properties.is_sub:
                add_results([(col_group_maps.get('kind') or _dummy)()])
            case 'type':
                add_results([(col_group_maps.get('type') or _dummy)()])
            case 'identity-relations':
                add_results((col_group_maps.get('identity') or _dummy_list)())
            case 'inline-relations':
                add_results((col_group_maps.get('inline') or _dummy_list)())
            case 'foreign-relations':
                add_results((col_group_maps.get('foreign') or _dummy_list)())
            case 'attributes' if concept_properties.permit_attributes:
                add_results((col_group_maps.get('attributes') or _dummy_list)())
    if appended_cols:
        add_results(appended_cols())

    return results, created_results
