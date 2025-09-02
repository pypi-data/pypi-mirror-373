from __future__ import annotations

import sqlalchemy as sa

from mitm_tooling.data_types import MITMDataType
from mitm_tooling.definition import MITM, ConceptName, get_mitm_def
from mitm_tooling.utilities.backports.sqlchemy_sql_views import create_view

from ...intermediate import HeaderEntry
from ...intermediate.header import Header
from ..common import (
    ConceptTablesDict,
    ConceptTypeTablesDict,
    SchemaName,
    SQLRepresentationSchema,
    ViewProperties,
)
from .common import (
    SQL_REPRESENTATION_DEFAULT_SCHEMA,
    has_type_tables,
    mk_concept_table_name,
    mk_type_table_name,
)
from .gen_columns import gen_within_concept_id_col
from .gen_schema_items import (
    gen_concept_table_fk_constraint,
    gen_foreign_relation_fk_constraints,
    gen_indices,
    gen_pk_constraint,
    gen_unique_constraint,
)
from .gen_tables import mk_table
from .gen_views import gen_denormalized_views, gen_sub_concept_views
from .meta_tables import mk_meta_tables


def mk_concept_table(
    meta: sa.MetaData,
    mitm: MITM,
    concept: ConceptName,
    target_schema: SchemaName | None = SQL_REPRESENTATION_DEFAULT_SCHEMA,
    skip_fk_constraints: bool = False,
):
    base_schema_item_generators = (
        gen_unique_constraint,
        gen_pk_constraint,
        gen_indices,
    )

    concept_table_schema_item_generators = (
        base_schema_item_generators + (gen_foreign_relation_fk_constraints,)
        if not skip_fk_constraints
        else base_schema_item_generators
    )

    mitm_def = get_mitm_def(mitm)
    concept_properties, concept_relations = mitm_def.get(concept)

    table_name = mk_concept_table_name(mitm, concept)

    def typ(concept_properties=concept_properties):
        return (
            concept_properties.typing_concept,
            sa.Column(concept_properties.typing_concept, MITMDataType.Text.sa_sql_type, nullable=False),
        )

    def identity(concept=concept):
        return [
            (name, sa.Column(name, dt.sa_sql_type, nullable=False))
            for name, dt in mitm_def.resolve_identity_type(concept).items()
        ]

    def inline(concept=concept):
        return [(name, sa.Column(name, dt.sa_sql_type)) for name, dt in mitm_def.resolve_inlined_types(concept).items()]

    def foreign(concept=concept):
        return [
            (name, sa.Column(name, dt.sa_sql_type))
            for _, resolved_fk in mitm_def.resolve_foreign_types(concept).items()
            for name, dt in resolved_fk.items()
        ]

    t, t_columns, t_ref_columns = mk_table(
        meta,
        mitm,
        concept,
        table_name,
        col_group_maps={
            'kind': lambda: ('kind', sa.Column('kind', MITMDataType.Text.sa_sql_type, nullable=False)),
            'type': typ,
            'identity': identity,
            'inline': inline,
            'foreign': foreign,
        },
        additional_column_generators=(gen_within_concept_id_col,),
        schema_item_generators=concept_table_schema_item_generators,
        target_schema=target_schema,
    )
    return t


def mk_type_table(
    meta: sa.MetaData,
    mitm: MITM,
    he: HeaderEntry,
    target_schema: SchemaName | None = SQL_REPRESENTATION_DEFAULT_SCHEMA,
    skip_fk_constraints: bool = False,
) -> sa.Table:
    he_concept = he.concept
    mitm_def = get_mitm_def(mitm)
    concept_properties, concept_relations = mitm_def.get(he_concept)
    table_name = mk_type_table_name(mitm, he_concept, he.type_name)

    base_schema_item_generators = (
        gen_unique_constraint,
        gen_pk_constraint,
        gen_indices,
    )

    type_table_schema_item_generators = (
        base_schema_item_generators
        + (
            gen_concept_table_fk_constraint,
            gen_foreign_relation_fk_constraints,
        )
        if not skip_fk_constraints
        else base_schema_item_generators
    )

    def typ(concept_properties=concept_properties):
        return (
            concept_properties.typing_concept,
            sa.Column(concept_properties.typing_concept, MITMDataType.Text.sa_sql_type, nullable=False),
        )

    def identity(he_concept=he_concept):
        return [
            (name, sa.Column(name, dt.sa_sql_type, nullable=False))
            for name, dt in mitm_def.resolve_identity_type(he_concept).items()
        ]

    def inline(he_concept=he_concept):
        return [
            (name, sa.Column(name, dt.sa_sql_type)) for name, dt in mitm_def.resolve_inlined_types(he_concept).items()
        ]

    def foreign(he_concept=he_concept):
        return [
            (name, sa.Column(name, dt.sa_sql_type))
            for _, resolved_fk in mitm_def.resolve_foreign_types(he_concept).items()
            for name, dt in resolved_fk.items()
        ]

    def attributes(he=he):
        return [(name, sa.Column(name, dt.sa_sql_type)) for name, dt in he.iter_attr_dtype_pairs()]

    t, t_columns, t_ref_columns = mk_table(
        meta,
        mitm,
        he_concept,
        table_name,
        {
            'kind': lambda: ('kind', sa.Column('kind', MITMDataType.Text.sa_sql_type, nullable=False)),
            'type': typ,
            'identity': identity,
            'inline': inline,
            'foreign': foreign,
            'attributes': attributes,
        },
        additional_column_generators=(gen_within_concept_id_col,),
        schema_item_generators=type_table_schema_item_generators,
        target_schema=target_schema,
    )
    return t


def mk_views(
    meta: sa.MetaData,
    header: Header,
    concept_tables: ConceptTablesDict,
    type_tables: ConceptTypeTablesDict,
    target_schema: SchemaName | None = SQL_REPRESENTATION_DEFAULT_SCHEMA,
) -> dict[str, tuple[sa.Table, ViewProperties]]:
    views = {}
    view_generators = (
        gen_sub_concept_views,
        gen_denormalized_views,
    )
    for generator in view_generators:
        for view_props in generator(header, concept_tables, type_tables):
            views[view_props.name] = (
                create_view(
                    view_props.name,
                    view_props.selectable,
                    meta,
                    schema=target_schema,
                    cascade_on_drop=view_props.cascade_on_drop,
                    replace=view_props.replace,
                ),
                view_props,
            )
    return views


def mk_sql_rep_schema(
    header: Header,
    target_schema: SchemaName | None = SQL_REPRESENTATION_DEFAULT_SCHEMA,
    skip_fk_constraints: bool = False,
    skip_views: bool = False,
    include_meta_tables: bool = True,
) -> SQLRepresentationSchema:
    """
    Generate an `SQLRepresentationSchema` from a `Header`.
    The canonical relational MITM representation requires the inclusion of the meta-tables and views.

    :param header: the header to generate the schema from
    :param target_schema: the name of the schema to create the tables in. By default, the `SQL_REPRESENTATION_DEFAULT_SCHEMA` will be used.
    :param skip_fk_constraints: whether to skip the generation of foreign key constraints. Defaults to False. FKs can be useful for some external tools, but they may make mutating the database more difficult.
    :param skip_views: whether to skip the generation of views. Defaults to False.
    :param include_meta_tables: whether to include the meta-tables. Defaults to True.
    :return:
    """

    mitm_def = get_mitm_def(header.mitm)
    meta = sa.MetaData(schema=target_schema)

    concept_tables: ConceptTablesDict = {}
    type_tables: ConceptTypeTablesDict = {}
    views: dict[str, tuple[sa.Table, ViewProperties]] = {}

    for concept in mitm_def.main_concepts:
        concept_tables[concept] = mk_concept_table(
            meta, header.mitm, concept, target_schema=target_schema, skip_fk_constraints=skip_fk_constraints
        )

    for he in header.header_entries:
        he_concept = he.concept
        if has_type_tables(mitm_def, he_concept):
            t = mk_type_table(meta, header.mitm, he, target_schema, skip_fk_constraints=skip_fk_constraints)

            if he_concept not in type_tables:
                type_tables[he_concept] = {}
            type_tables[he_concept][he.type_name] = t

    if not skip_views:
        views = mk_views(meta, header, concept_tables, type_tables, target_schema=target_schema)

    meta_tables = None
    if include_meta_tables:
        meta_tables = mk_meta_tables(meta, target_schema=target_schema)

    return SQLRepresentationSchema(
        mitm=header.mitm,
        sa_meta=meta,
        meta_tables=meta_tables,
        concept_tables=concept_tables,
        type_tables=type_tables,
        views=views,
    )
