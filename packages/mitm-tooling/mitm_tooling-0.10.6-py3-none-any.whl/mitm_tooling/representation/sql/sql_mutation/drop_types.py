from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

import sqlalchemy as sa

from mitm_tooling.definition import ConceptName, MITMDefinition, TypeName, get_mitm_def

from ..common import (
    SQLRepresentationInstanceUpdateError,
    SQLRepresentationSchemaUpdateError,
)
from ..sql_representation import SQLRepresentationSchema


def _drop_type(
    conn: sa.Connection,
    sql_rep_schema: SQLRepresentationSchema,
    mitm_def: MITMDefinition,
    concept: ConceptName,
    type_name: TypeName,
    instances_only: bool = False,
):
    # first drop the type-specific table if it exists
    if (t_type := sql_rep_schema.get_type_table(concept, type_name)) is not None:
        if instances_only:
            conn.execute(t_type.delete())
        else:
            t_type.drop(conn)

    # then drop the rows in the parent concept table
    main_concept = mitm_def.get_parent(concept)
    properties = mitm_def.get_properties(main_concept)
    if (t_concept := sql_rep_schema.get_concept_table(main_concept)) is not None:
        typing_concept = properties.typing_concept
        deletion = t_concept.delete().where(t_concept.columns[typing_concept] == type_name)
        conn.execute(deletion)


def _drop_types(
    conn: sa.Connection,
    sql_rep_schema: SQLRepresentationSchema,
    types_to_drop: Iterable[tuple[ConceptName, TypeName]],
    drop_from_meta_tables: bool = True,
    instances_only: bool = False,
):
    mitm_def = get_mitm_def(sql_rep_schema.mitm)
    structured_drops = defaultdict(list)
    for concept, type_name in types_to_drop:
        structured_drops[concept].append(type_name)

    for concept, type_names in structured_drops.items():
        properties = mitm_def.get_properties(concept)

        for type_name in type_names:
            try:
                _drop_type(conn, sql_rep_schema, mitm_def, concept, type_name, instances_only=instances_only)
            except Exception as e:
                raise SQLRepresentationSchemaUpdateError(f'Dropping type {concept}:{type_name} failed') from e
        if not instances_only and drop_from_meta_tables:
            if (meta_tables := sql_rep_schema.meta_tables) is not None:
                try:
                    kind = properties.kind
                    deletion_child = meta_tables.type_attributes.delete().where(
                        meta_tables.type_attributes.c['kind'] == kind,
                        meta_tables.type_attributes.c['type_name'].in_(type_names),
                    )
                    deletion_parent = meta_tables.types.delete().where(
                        meta_tables.types.c['kind'] == kind, meta_tables.types.c['type_name'].in_(type_names)
                    )
                    conn.execute(deletion_child)
                    conn.execute(deletion_parent)
                except Exception as e:
                    raise SQLRepresentationInstanceUpdateError(
                        f'Dropping types {concept}:{type_names} from meta tables failed'
                    ) from e
