from __future__ import annotations

from collections.abc import Generator

import sqlalchemy as sa

from mitm_tooling.definition import get_mitm_def
from mitm_tooling.utilities.sql_utils import str_to_sql_identifier

from ...intermediate.header import Header
from ..common import (
    ConceptTablesDict,
    ConceptTypeTablesDict,
    ViewProperties,
)
from .common import (
    MitMDBViewsGenerator,
    _prefix_col_name,
    has_type_tables,
    mk_concept_table_name,
)


def gen_denormalized_views(
    header: Header, concept_tables: ConceptTablesDict, type_tables: ConceptTypeTablesDict
) -> Generator[ViewProperties, None, None]:
    mitm = header.mitm
    mitm_def = get_mitm_def(mitm)

    for main_concept in mitm_def.main_concepts:
        for concept in mitm_def.get_leaves(main_concept):
            view_name = mk_concept_table_name(mitm, concept) + '_denormalized_view'
            q = None
            if has_type_tables(mitm_def, concept):
                selections = []

                for leaf_concept in mitm_def.get_leaves(concept):
                    if concept_type_tables := type_tables.get(leaf_concept):
                        concept_properties, concept_relations = mitm_def.get(leaf_concept)
                        # col_sets = [{(c.name, str(c.type)) for c in t.columns} for t in concept_type_tables.values()]

                        # shared_cols, _ = map_col_groups(
                        #     mitm_def,
                        #     concept,
                        #     {
                        #         'kind': lambda: 'kind',
                        #         'type': lambda: concept_properties.typing_concept,
                        #         'identity': lambda: list(concept_relations.identity),
                        #     },
                        # )
                        shared_cols = None
                        for type_name, t in concept_type_tables.items():
                            he = header.get(leaf_concept, type_name)
                            t_cols = {c.name for c in t.columns if c.name not in he.attributes}
                            if shared_cols is None:
                                shared_cols = t_cols
                            else:
                                shared_cols &= t_cols

                        per_type_cols = [
                            (type_name, _prefix_col_name(str_to_sql_identifier(type_name), c.name), c)
                            for type_name, t in concept_type_tables.items()
                            for c in t.columns
                            if c.name not in shared_cols
                        ]

                        for type_name, type_t in concept_type_tables.items():
                            selection = [type_t.columns.get(c) for c in shared_cols]

                            for _type_name, col_label, sa_col in per_type_cols:
                                if type_name == _type_name:
                                    selection.append(sa_col.label(col_label))
                                else:
                                    selection.append(sa.null().label(col_label))

                            selections.append(sa.select(*selection))

                if selections:
                    q = sa.union_all(*selections).subquery()
            else:
                if (concept_t := concept_tables.get(concept)) is not None:
                    # base_cols = {(c.name, str(c.type)) for c in concept_t.columns}
                    q = sa.select(concept_t)

            if q is not None:
                yield ViewProperties(name=view_name, selectable=q, is_type_dependant=True)


def gen_sub_concept_views(
    header: Header, concept_tables: ConceptTablesDict, type_tables: ConceptTypeTablesDict
) -> Generator[ViewProperties, None, None]:
    mitm_def = header.mitm_def
    for parent_concept, subs in mitm_def.sub_concept_map.items():
        if (concept_t := concept_tables.get(parent_concept)) is not None:
            for sub in subs:
                view_name = mk_concept_table_name(header.mitm, sub) + '_view'
                k = mitm_def.get_properties(sub).key
                q = sa.select(concept_t).where(concept_t.columns['kind'] == k)
                yield ViewProperties(name=view_name, selectable=q, is_type_dependant=False)


# for typing
view_generators: tuple[MitMDBViewsGenerator, ...] = (
    gen_sub_concept_views,
    gen_denormalized_views,
)
