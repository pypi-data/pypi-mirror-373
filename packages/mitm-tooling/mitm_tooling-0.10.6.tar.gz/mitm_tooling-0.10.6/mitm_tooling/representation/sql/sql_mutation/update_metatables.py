from __future__ import annotations

from mitm_tooling.utilities.sql_utils import EngineOrConnection, use_nested_conn

from ...intermediate.header import Header
from ..common import (
    SQLRepresentationMetaUpdateError,
)
from ..sql_representation import SQLRepresentationSchema


def insert_meta_data(bind: EngineOrConnection, sql_rep_schema: SQLRepresentationSchema, header: Header) -> None:
    if (meta_tables := sql_rep_schema.meta_tables) is not None:
        mitm_def_json = header.mitm_def.model_dump(mode='json', by_alias=True, exclude_unset=True, exclude_none=True)

        try:
            with use_nested_conn(bind) as conn:
                conn.execute(
                    meta_tables.key_value.insert().values(
                        [{'key': 'mitm', 'value': header.mitm}, {'key': 'mitm_def', 'value': mitm_def_json}]
                    )
                )

                if header.header_entries:
                    conn.execute(
                        meta_tables.types.insert().values(
                            [
                                {
                                    'kind': he.kind,
                                    'type': he.type_name,
                                    'concept': he.concept,
                                    'type_table_name': t.name
                                    if (t := sql_rep_schema.type_tables.get(he.concept, {}).get(he.type_name))
                                    is not None
                                    else None,
                                }
                                for he in header.header_entries
                            ]
                        )
                    )

                    conn.execute(
                        meta_tables.type_attributes.insert().values(
                            [
                                {
                                    'kind': he.kind,
                                    'type': he.type_name,
                                    'attribute_order': i,
                                    'attribute_name': a,
                                    'attribute_dtype': str(dt),
                                }
                                for he in header.header_entries
                                for i, (a, dt) in enumerate(he.iter_attr_dtype_pairs())
                            ]
                        )
                    )
                # conn.commit()
        except Exception as e:
            raise SQLRepresentationMetaUpdateError('Insertion of data into meta tables failed') from e


def drop_meta_data(bind: EngineOrConnection, sql_rep_schema: SQLRepresentationSchema) -> None:
    if (meta_tables := sql_rep_schema.meta_tables) is not None:
        try:
            with use_nested_conn(bind) as conn:
                conn.execute(meta_tables.key_value.delete())
                conn.execute(meta_tables.type_attributes.delete())
                conn.execute(meta_tables.types.delete())
                # meta_tables.key_value.drop(conn)
                # meta_tables.type_attributes.drop(conn)
                # meta_tables.types.drop(conn)
                # conn.commit()
        except Exception as e:
            raise SQLRepresentationMetaUpdateError('Clearing of meta tables failed') from e


def update_meta_data(bind: EngineOrConnection, sql_rep_schema: SQLRepresentationSchema, header: Header) -> None:
    drop_meta_data(bind, sql_rep_schema)
    insert_meta_data(bind, sql_rep_schema, header)
