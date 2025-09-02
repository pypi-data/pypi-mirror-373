from __future__ import annotations

from collections.abc import Callable, Generator

import sqlalchemy as sa
from sqlalchemy.sql.schema import SchemaItem

from mitm_tooling.definition import MITM, ConceptName, MITMDefinition, RelationName, get_mitm_def
from mitm_tooling.definition.definition_tools import map_col_groups
from mitm_tooling.utilities.sql_utils import str_to_sql_identifier

from ...intermediate.header import Header
from ..common import (
    ColumnsDict,
    ConceptTablesDict,
    ConceptTypeTablesDict,
    SchemaName,
    TableName,
    ViewProperties,
)

SQL_REPRESENTATION_DEFAULT_SCHEMA = 'main'

MitMConceptSchemaItemGenerator = Callable[
    [MITM, ConceptName, SchemaName, TableName, ColumnsDict, ColumnsDict | None], Generator[SchemaItem, None, None]
]
MitMConceptColumnGenerator = Callable[[MITM, ConceptName], Generator[tuple[str, sa.Column], None, None]]


MitMDBViewsGenerator = Callable[
    [Header, ConceptTablesDict, ConceptTypeTablesDict], Generator[ViewProperties, None, None]
]


def _prefix_col_name(prefix: str, name: str) -> str:
    return f'{prefix}_{name}'


def _get_unique_id_col_name(prefix: str | None = None) -> str:
    return '__' + ((prefix + '_') if prefix else '') + 'id'


def mk_within_concept_id_col_name(mitm: MITM, concept: ConceptName) -> str:
    parent_concept = get_mitm_def(mitm).get_parent(concept)
    return _get_unique_id_col_name(parent_concept)


def mk_concept_table_name(mitm: MITM, concept: ConceptName) -> TableName:
    return get_mitm_def(mitm).get_properties(concept).plural


def mk_type_table_name(mitm: MITM, concept: ConceptName, type_name: RelationName) -> TableName:
    type_name_identifier = str_to_sql_identifier(type_name)
    return get_mitm_def(mitm).get_properties(concept).key + '_' + type_name_identifier


def mk_link_table_name(mitm: MITM, concept: ConceptName, type_name: RelationName, fk_name: RelationName) -> TableName:
    fk_name_identifier = str_to_sql_identifier(type_name)
    return mk_type_table_name(mitm, concept, type_name) + '_' + fk_name_identifier


def has_type_tables(mitm_def: MITMDefinition, concept: ConceptName) -> bool:
    return mitm_def.get_properties(concept).permit_attributes


def has_natural_pk(mitm_def: MITMDefinition, concept: ConceptName) -> bool:
    return len(mitm_def.get_identity(concept)) > 0


def pick_table_pk(mitm: MITM, concept: ConceptName, created_columns: ColumnsDict) -> ColumnsDict | None:
    mitm_def = get_mitm_def(mitm)
    concept_properties, concept_relations = mitm_def.get(concept)

    prepended_cols = None
    if not has_natural_pk(mitm_def, concept):

        def prepended_cols():
            return [mk_within_concept_id_col_name(mitm, concept)]

    names, mapped_names = map_col_groups(
        mitm_def,
        concept,
        {
            'kind': lambda: 'kind',
            'type': lambda: concept_properties.typing_concept,
            'identity': lambda: list(concept_relations.identity),
        },
        prepended_cols=prepended_cols,
    )

    return {n: created_columns[n] for n in names}
