from __future__ import annotations

from collections.abc import Generator

import sqlalchemy as sa

from mitm_tooling.definition import MITM, ConceptName, get_mitm_def
from mitm_tooling.utilities.sql_utils import qualify

from ..common import (
    ColumnsDict,
    SchemaName,
    TableName,
)
from .common import (
    MitMConceptSchemaItemGenerator,
    mk_concept_table_name,
    mk_within_concept_id_col_name,
)


def gen_unique_constraint(
    mitm: MITM,
    concept: ConceptName,
    schema_name: SchemaName,
    table_name: TableName,
    created_columns: ColumnsDict,
    pk_columns: ColumnsDict | None,
) -> Generator[sa.sql.schema.SchemaItem, None, None]:
    yield sa.UniqueConstraint(*pk_columns.values())


def gen_pk_constraint(
    mitm: MITM,
    concept: ConceptName,
    schema_name: SchemaName,
    table_name: TableName,
    created_columns: ColumnsDict,
    pk_columns: ColumnsDict | None,
) -> Generator[sa.sql.schema.SchemaItem, None, None]:
    yield sa.PrimaryKeyConstraint(*pk_columns.values())


def gen_indices(
    mitm: MITM,
    concept: ConceptName,
    schema_name: SchemaName,
    table_name: TableName,
    created_columns: ColumnsDict,
    pk_columns: ColumnsDict | None,
) -> Generator[sa.sql.schema.SchemaItem, None, None]:
    n = mk_within_concept_id_col_name(mitm, concept)
    if n in created_columns:
        yield sa.Index(f'{table_name}.{n}.index', created_columns[n], unique=True)
    yield sa.Index(f'{table_name}.index', *pk_columns.values(), unique=True)


def gen_foreign_relation_fk_constraints(
    mitm: MITM,
    concept: ConceptName,
    schema_name: SchemaName,
    table_name: TableName,
    created_columns: ColumnsDict,
    pk_columns: ColumnsDict | None,
) -> Generator[sa.sql.schema.SchemaItem, None, None]:
    mitm_def = get_mitm_def(mitm)
    _, concept_relations = mitm_def.get(concept)
    for fk_name, fk_info in concept_relations.foreign.items():
        cols, refcols = zip(*fk_info.fk_relations.items(), strict=False)
        fkc = sa.ForeignKeyConstraint(
            name=fk_name,
            columns=[created_columns[c] for c in cols],
            refcolumns=[
                qualify(schema=schema_name, table=mk_concept_table_name(mitm, fk_info.target_concept), column=c)
                for c in refcols
            ],
        )
        yield fkc


def gen_concept_table_fk_constraint(
    mitm: MITM,
    concept: ConceptName,
    schema_name: SchemaName,
    table_name: TableName,
    created_columns: ColumnsDict,
    pk_columns: ColumnsDict | None,
) -> Generator[sa.sql.schema.SchemaItem, None, None]:
    mitm_def = get_mitm_def(mitm)
    if pk_columns:
        parent_concept = mitm_def.get_parent(concept)
        parent_table = mk_concept_table_name(mitm, parent_concept)
        if table_name == parent_table:
            return
        cols, refcols = zip(
            *((c, qualify(schema=schema_name, table=parent_table, column=s)) for s, c in pk_columns.items()),
            strict=False,
        )
        yield sa.ForeignKeyConstraint(name='parent', columns=cols, refcolumns=refcols)


# for typing
schema_item_generators: tuple[MitMConceptSchemaItemGenerator, ...] = (
    gen_unique_constraint,
    gen_pk_constraint,
    gen_indices,
    gen_concept_table_fk_constraint,
    gen_foreign_relation_fk_constraints,
)
