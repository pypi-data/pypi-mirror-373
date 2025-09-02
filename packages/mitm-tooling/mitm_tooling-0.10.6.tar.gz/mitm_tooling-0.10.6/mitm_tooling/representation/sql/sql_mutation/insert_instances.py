from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Sequence
from typing import Any

import pandas as pd
import pydantic
import sqlalchemy as sa
from sqlalchemy import func

from mitm_tooling.definition import ConceptName, MITMDefinition, TypeName, get_mitm_def
from mitm_tooling.utilities.sql_utils import AnyDBBind, use_nested_conn

from ...df import TypedMITMDataFrameStream
from ...intermediate.header import HeaderEntry
from ..common import (
    SQLRepresentationInstanceUpdateError,
)
from ..sql_representation import SQLRepresentationSchema
from ..sql_representation.common import has_type_tables, mk_within_concept_id_col_name


def _df_to_records(
    df: pd.DataFrame, cols: Sequence[str], additional_cols: dict[str, Any] | None = None
) -> list[dict[str, Any]]:
    if additional_cols:
        df = df.assign(**additional_cols)
    return df[[c for c in cols if c in df.columns]].to_dict('records')


def _df_to_table_records(
    df: pd.DataFrame, table: sa.Table, additional_cols: dict[str, Any] | None = None
) -> list[dict[str, Any]]:
    return _df_to_records(df, [c.name for c in table.columns], additional_cols=additional_cols)


def _insert_type_df(
    conn: sa.Connection,
    sql_rep_schema: SQLRepresentationSchema,
    mitm_def: MITMDefinition,
    concept: ConceptName,
    type_name: TypeName,
    type_df: pd.DataFrame,
    artificial_id_offset: int | None = None,
) -> tuple[int, int]:
    parent_concept = mitm_def.get_parent(concept)
    inserted_rows, no_instances = 0, 0
    if (t_concept := sql_rep_schema.get_concept_table(parent_concept)) is not None:
        # if not has_natural_pk(mitm, concept):
        # TODO not pretty..
        # ideally, I'd use the returned "inserted_pk"
        # values from the bulk insertion with an autoincrement id col
        # but apparently almost no DBABI drivers support this
        no_instances = len(type_df)
        concept_id_col_name = mk_within_concept_id_col_name(sql_rep_schema.mitm, parent_concept)
        max_id = conn.execute(sa.select(func.max(t_concept.columns[concept_id_col_name]))).scalar() or 0
        start_id = max_id + (artificial_id_offset or 0) + 1
        artificial_ids = pd.RangeIndex(start=start_id, stop=start_id + no_instances, name=concept_id_col_name)
        # type_df[concept_id_col_name] = artificial_ids
        type_df = type_df.assign(**{concept_id_col_name: artificial_ids})
        conn.execute(t_concept.insert(), _df_to_table_records(type_df, t_concept))
        inserted_rows += no_instances

    if has_type_tables(mitm_def, concept):
        if (t_type := sql_rep_schema.get_type_table(concept, type_name)) is not None:
            # generated_ids = conn.execute(sa.select(t_concept.columns[concept_id_col_name])).scalars()
            conn.execute(t_type.insert(), _df_to_table_records(type_df, t_type))
            inserted_rows += no_instances
    return no_instances, inserted_rows


def _insert_type_dfs(
    conn: sa.Connection,
    sql_rep_schema: SQLRepresentationSchema,
    mitm_def: MITMDefinition,
    concept: ConceptName,
    typed_dfs: Iterable[tuple[TypeName, HeaderEntry, Iterable[pd.DataFrame]]],
) -> tuple[list[HeaderEntry], int, int]:
    total_inserted_instances, total_inserted_rows = 0, 0
    offsets = defaultdict(int)
    inserted_types = []
    for type_name, he, type_dfs in typed_dfs:
        inserted_types.append(he)
        for type_df in type_dfs:
            try:
                inserted_instances, inserted_rows = _insert_type_df(
                    conn, sql_rep_schema, mitm_def, concept, type_name, type_df, artificial_id_offset=offsets[type_name]
                )
            except Exception as e:
                raise SQLRepresentationInstanceUpdateError(
                    f'Insertion of instances of type {concept}:{type_name} failed'
                ) from e
            offsets[type_name] += inserted_instances
            total_inserted_instances += inserted_instances
            total_inserted_rows += inserted_rows
    return inserted_types, total_inserted_instances, total_inserted_rows


class SQLRepInsertionResult(pydantic.BaseModel):
    inserted_types: list[HeaderEntry]
    inserted_instances: int
    inserted_rows: int


def insert_instances(
    bind: AnyDBBind, sql_rep_schema: SQLRepresentationSchema, instances: TypedMITMDataFrameStream
) -> SQLRepInsertionResult:
    """
    Insert a stream of MITM dataframes into a relational database, with tables (and views) defined by the given SQL representation schema.
    This assumes that the schema is already created. In particular, this implies that the instances to be inserted cannot be of any type not yet present in the schema.

    Note that if this function is called with a `bind` of type `Connection` (as opposed to a `Engine`),
    a manual commit may be required afterward to persist the changes.
    Internally, the insertions are performed in a nested transaction.

    :param bind: a bind to the database to insert into
    :param sql_rep_schema: the SQL representation schema to use
    :param instances: a stream of (typed) instances to insert
    :return: a summary of the inserted instances
    """

    total_inserted_instances, total_inserted_rows = 0, 0
    total_inserted_types = []
    mitm_def = get_mitm_def(sql_rep_schema.mitm)
    try:
        with use_nested_conn(bind) as conn:
            for concept, typed_dfs in instances:
                inserted_types, inserted_instances, inserted_rows = _insert_type_dfs(
                    conn, sql_rep_schema, mitm_def, concept, typed_dfs
                )
                total_inserted_instances += inserted_instances
                total_inserted_rows += inserted_rows
                total_inserted_types.extend(inserted_types)
            # conn.commit()
    except Exception as e:
        raise SQLRepresentationInstanceUpdateError('Insertion of instances into SQL representation failed') from e
    return SQLRepInsertionResult(
        inserted_instances=total_inserted_instances,
        inserted_rows=total_inserted_rows,
        inserted_types=total_inserted_types,
    )
