from __future__ import annotations

import sqlalchemy as sa

from mitm_tooling.data_types import MITMDataType

from ..common import (
    HeaderMetaTableName,
    HeaderMetaTables,
    SchemaName,
)
from .common import (
    SQL_REPRESENTATION_DEFAULT_SCHEMA,
)


def mk_meta_tables(
    meta: sa.MetaData, target_schema: SchemaName | None = SQL_REPRESENTATION_DEFAULT_SCHEMA
) -> HeaderMetaTables:
    header_meta_types = sa.Table(
        HeaderMetaTableName.Types,
        meta,
        sa.Column('kind', MITMDataType.Text.sa_sql_type, primary_key=True),
        sa.Column('type', MITMDataType.Text.sa_sql_type, primary_key=True),
        sa.Column('concept', MITMDataType.Text.sa_sql_type),
        sa.Column('type_table_name', MITMDataType.Text.sa_sql_type, nullable=True),
        # this is mainly provided as a benefit for other tooling, as this package directly uses the deterministic `mk_type_table_name` function
        schema=target_schema,
    )
    header_meta_type_attributes = sa.Table(
        HeaderMetaTableName.TypeAttributes,
        meta,
        sa.Column('kind', MITMDataType.Text.sa_sql_type, primary_key=True),
        sa.Column('type', MITMDataType.Text.sa_sql_type, primary_key=True),
        sa.Column('attribute_order', MITMDataType.Integer.sa_sql_type, primary_key=True),
        sa.Column('attribute_name', MITMDataType.Text.sa_sql_type),
        sa.Column('attribute_dtype', MITMDataType.Text.sa_sql_type),
        sa.ForeignKeyConstraint(
            name='header_meta_type',
            columns=['kind', 'type'],
            refcolumns=[header_meta_types.c.kind, header_meta_types.c.type],
        ),
        schema=target_schema,
    )

    header_meta_key_value = sa.Table(
        HeaderMetaTableName.KeyValue,
        meta,
        sa.Column('key', MITMDataType.Text.sa_sql_type, primary_key=True),
        sa.Column('value', MITMDataType.Json.sa_sql_type),
        schema=target_schema,
    )

    return HeaderMetaTables(
        key_value=header_meta_key_value, types=header_meta_types, type_attributes=header_meta_type_attributes
    )
