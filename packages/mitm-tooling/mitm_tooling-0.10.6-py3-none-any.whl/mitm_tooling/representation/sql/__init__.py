"""
A relational representation of MITM data via a collection of tables and views.
It is most suitable for data storage and ETL-pipeline generation.
"""

from ..common import ColumnName
from . import sql_mutation, sql_representation
from .common import (
    QualifiedTableName,
    Queryable,
    SchemaName,
    ShortTableIdentifier,
    SQLRepresentationDropError,
    SQLRepresentationError,
    SQLRepresentationInstanceUpdateError,
    SQLRepresentationMetaUpdateError,
    SQLRepresentationSchema,
    SQLRepresentationSchemaUpdateError,
    TableName,
)
from .sql_mutation import (
    SQLRepInsertionResult,
    append_data,
    create_schema,
    drop_data,
    drop_schema,
    drop_type_instances,
    insert_data,
    insert_instances,
    mutate_schema,
)
from .sql_representation import SQL_REPRESENTATION_DEFAULT_SCHEMA, mk_sql_rep_schema

__all__ = [
    'ColumnName',
    'TableName',
    'SchemaName',
    'QualifiedTableName',
    'ShortTableIdentifier',
    'Queryable',
    'SQL_REPRESENTATION_DEFAULT_SCHEMA',
    'SQLRepresentationSchema',
    'mk_sql_rep_schema',
    'SQLRepInsertionResult',
    'SQLRepresentationError',
    'SQLRepresentationSchemaUpdateError',
    'SQLRepresentationMetaUpdateError',
    'SQLRepresentationInstanceUpdateError',
    'SQLRepresentationDropError',
    'drop_data',
    'drop_type_instances',
    'insert_instances',
    'insert_data',
    'append_data',
    'mutate_schema',
    'create_schema',
    'drop_schema',
    'sql_mutation',
    'sql_representation',
]
