from __future__ import annotations

from collections.abc import Iterable

import sqlalchemy as sa

from mitm_tooling.definition import MITM, ConceptName, get_mitm_def
from mitm_tooling.definition.definition_tools import ColGroupMaps, map_col_groups

from ..common import (
    ColumnsDict,
    SchemaName,
    TableName,
)
from .common import (
    SQL_REPRESENTATION_DEFAULT_SCHEMA,
    MitMConceptColumnGenerator,
    MitMConceptSchemaItemGenerator,
    pick_table_pk,
)
from .gen_columns import gen_within_concept_id_col
from .gen_schema_items import (
    gen_indices,
    gen_pk_constraint,
    gen_unique_constraint,
)


def mk_table(
    meta: sa.MetaData,
    mitm: MITM,
    concept: ConceptName,
    table_name: TableName,
    col_group_maps: ColGroupMaps[sa.Column],
    additional_column_generators: Iterable[MitMConceptColumnGenerator] | None = (gen_within_concept_id_col,),
    schema_item_generators: Iterable[MitMConceptSchemaItemGenerator] | None = (
        gen_unique_constraint,
        gen_pk_constraint,
        gen_indices,
    ),
    target_schema: SchemaName | None = SQL_REPRESENTATION_DEFAULT_SCHEMA,
) -> tuple[sa.Table, ColumnsDict, ColumnsDict]:
    mitm_def = get_mitm_def(mitm)

    prepended_cols = None
    if additional_column_generators is not None:

        def prepended_cols():
            return [c for generator in additional_column_generators for c in generator(mitm, concept)]

    columns, created_columns = map_col_groups(
        mitm_def, concept, col_group_maps, prepended_cols=prepended_cols, ensure_unique=True
    )

    pk_cols = pick_table_pk(mitm, concept, created_columns)

    schema_items: list[sa.sql.schema.SchemaItem] = []
    if schema_item_generators is not None:
        for generator in schema_item_generators:
            schema_items.extend(generator(mitm, concept, target_schema, table_name, created_columns, pk_cols))

    return sa.Table(table_name, meta, *columns, *schema_items, schema=target_schema), created_columns, pk_cols
