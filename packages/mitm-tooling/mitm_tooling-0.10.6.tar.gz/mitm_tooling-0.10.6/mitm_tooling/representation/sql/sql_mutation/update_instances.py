from __future__ import annotations

import itertools
from typing import Any

import sqlalchemy as sa
from sqlalchemy import and_, bindparam, case, update

from mitm_tooling.definition import ConceptName, TypeName, get_mitm_def

from ...common import ColumnName
from ..sql_representation import SQLRepresentationSchema
from ..sql_representation.common import has_type_tables


def _update_instances_small(
    conn: sa.Connection,
    sql_rep_schema: SQLRepresentationSchema,
    concept: ConceptName,
    type_name: TypeName,
    updates: dict[tuple[Any, ...], dict[ColumnName, Any]],
):
    """
    Untested

    :param conn:
    :param sql_rep_schema:
    :param concept:
    :param type_name:
    :param updates:
    :return:
    """
    if has_type_tables(get_mitm_def(sql_rep_schema.mitm), concept):
        modified_table = sql_rep_schema.get_type_table(concept, type_name)
    else:
        modified_table = sql_rep_schema.get_concept_table(concept)

    if modified_table is None:
        return False

    # Filter out empty updates
    non_empty_updates = {pk: data for pk, data in updates.items() if data}
    if not non_empty_updates:
        return True

    pk_cols = modified_table.primary_key.columns
    pk_col_names = [c.name for c in pk_cols]

    # Collect all columns being updated
    all_updated_cols = set()
    for update_dict in non_empty_updates.values():
        all_updated_cols |= set(update_dict.keys())

    # Prepare bindparams and CASE expressions
    params = {}
    values_dict = {}

    for idx, (pk_tuple, update_dict) in enumerate(non_empty_updates.items()):
        # Add PK bindparams with "pk_" prefix
        for pk_col, pk_val in zip(pk_col_names, pk_tuple, strict=False):
            params[f'pk_{pk_col}_{idx}'] = pk_val

        # Add update bindparams with "val_" prefix
        for col_name, value in update_dict.items():
            params[f'val_{col_name}_{idx}'] = value

    # Build CASE expressions for each updated column
    for col_name in all_updated_cols:
        whens = []
        for idx, (_, update_dict) in enumerate(non_empty_updates.items()):
            if col_name not in update_dict:
                continue

            # Create condition for composite PK match
            pk_conditions = and_(*[modified_table.c[pk] == bindparam(f'pk_{pk}_{idx}') for pk in pk_col_names])
            whens.append((pk_conditions, bindparam(f'val_{col_name}_{idx}')))

        # Only add CASE expression if there are updates for this column
        if whens:
            values_dict[col_name] = case(*whens, else_=modified_table.c[col_name])

    # Execute update if we have columns to modify
    if values_dict:
        update_stmt = update(modified_table).values(values_dict)
        conn.execute(update_stmt, params)

    return True


def _update_instances(
    conn: sa.Connection,
    sql_rep_schema: SQLRepresentationSchema,
    concept: ConceptName,
    type_name: TypeName,
    updates: dict[tuple[Any, ...], dict[ColumnName, Any]],
):
    """
    Untested

    :param conn:
    :param sql_rep_schema:
    :param concept:
    :param type_name:
    :param updates:
    :return:
    """
    if has_type_tables(get_mitm_def(sql_rep_schema.mitm), concept):
        modified_table = sql_rep_schema.get_type_table(concept, type_name)
    else:
        modified_table = sql_rep_schema.get_concept_table(concept)

    if modified_table is not None:
        pk_col_names = [c.name for c in modified_table.primary_key.columns]
        pk_bindparams = [bindparam(c.name, type_=c.type).label(c.name) for c in modified_table.primary_key.columns]

        updated_col_names = set(itertools.chain(*updates.values()))  # union, consider intersection
        updated_cols = [modified_table.columns[n] for n in updated_col_names]

        updated_col_bindparams = [bindparam(c.name, type_=c.type).label(c.name) for c in updated_cols]

        update_data = [{n: x for n, x in zip(pk_col_names, k, strict=False)} | v for k, v in updates.items()]

        values_table = sa.select(*pk_bindparams, *updated_col_bindparams).values(update_data).alias('updates')

        update_stmt = (
            modified_table.update()
            .where(*(modified_table.c[n] == values_table.c[n] for n in pk_col_names))
            .values(**{n: values_table.c[n] for n in updated_col_names})
        )

        conn.execute(update_stmt)
        return True
    return False
