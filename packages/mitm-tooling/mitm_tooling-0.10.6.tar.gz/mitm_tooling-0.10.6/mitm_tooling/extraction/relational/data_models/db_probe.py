import logging
from typing import Any

import pydantic
from pydantic import Field, NonNegativeInt

from mitm_tooling.data_types import MITMDataType
from mitm_tooling.representation import ColumnName
from mitm_tooling.representation.sql import SchemaName, ShortTableIdentifier, TableName

from .db_meta import DBMetaInfo, DBMetaInfoBase, TableMetaInfoBase
from .probe_models import SampleSummary

logger = logging.getLogger(__name__)


class TableProbeMinimal(pydantic.BaseModel):
    """
    This model represents a probe of a table in a relational database.
    It is created from a sample of table rows and contains information about the inferred column types and type-appropriate column value summaries.
    It is serializable and can be used for exchange.
    """

    row_count: NonNegativeInt
    inferred_types: dict[ColumnName, MITMDataType]
    sample_summaries: dict[ColumnName, SampleSummary]


class TableProbeBase(TableProbeMinimal):
    """
    This model represents a probe of a table in a relational database.
    It is created from a sample of table rows and contains information about the inferred column types and type-appropriate column value summaries.
    Additionally, it holds structural information in the form of a `TableMetaInfoBase` object, as well as a dictionary of sampled values for each column in the table.
    This means it could be non-serializable, however, any values can be "sanitized" by converting them into strings.
    """

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    table_meta: TableMetaInfoBase
    sampled_values: dict[ColumnName, list[Any]]


class TableProbe(TableProbeBase): ...


class DBProbeMinimal(pydantic.BaseModel):
    """
    This model represents a probe of a relational database, via a structured collection of table probes.
    It is serializable and can be used for exchange.
    """

    db_table_probes: dict[SchemaName, dict[TableName, TableProbeMinimal]] = Field(default_factory=dict)

    @property
    def table_probes(self) -> dict[ShortTableIdentifier, TableProbeMinimal]:
        return {
            (schema_name, table_name): tp
            for schema_name, schema_probes in self.db_table_probes.items()
            for table_name, tp in schema_probes.items()
        }


class DBProbeBase(DBProbeMinimal):
    """
    This model represents a probe of a relational database, via a structured collection of table probes.
    It additionally holds structural information in the form of a `DBMetaInfoBase` object.
    Depending on the `TableProbeBases`, it is serializable and could be used for exchange.
    """

    db_meta: DBMetaInfoBase
    db_table_probes: dict[SchemaName, dict[TableName, TableProbeBase]] = Field(default_factory=dict)

    @property
    def table_probes(self) -> dict[ShortTableIdentifier, TableProbeBase]:
        return {
            (schema_name, table_name): tp
            for schema_name, schema_probes in self.db_table_probes.items()
            for table_name, tp in schema_probes.items()
        }


class DBProbe(DBProbeBase):
    """
    This model represents a probe of a relational database, via a structured collection of table probes.
    It additionally holds structural information in the form of a full `DBMetaInfo` object.
    It is therefore not serializable.
    """

    db_meta: DBMetaInfo
    db_table_probes: dict[SchemaName, dict[TableName, TableProbe]] = Field(default_factory=dict)

    @property
    def table_probes(self) -> dict[ShortTableIdentifier, TableProbe]:
        return {
            (schema_name, table_name): tp
            for schema_name, schema_probes in self.db_table_probes.items()
            for table_name, tp in schema_probes.items()
        }

    def update_meta(self, new_db_meta: DBMetaInfo):
        if self.db_meta is not None:
            remaining_probes = {}
            for schema_name, existing_tables in self.db_meta.db_structure.items():
                if schema_name not in self.db_table_probes:
                    continue

                if (new_tables := new_db_meta.db_structure.get(schema_name)) is not None:
                    schema_local_probes = {}
                    for table_name, existing_table in existing_tables.items():
                        if table_name not in self.db_table_probes[schema_name]:
                            continue

                        if ((table := new_tables.get(table_name)) is not None) and table == existing_table:
                            schema_local_probes[table_name] = self.db_table_probes[schema_name][table_name]
                        else:
                            logger.info(f'Removed table probe of {schema_name}.{table_name} due to metadata refresh.')

                    if len(schema_local_probes) > 0:
                        remaining_probes[schema_name] = schema_local_probes

            self.db_table_probes = remaining_probes
        self.db_meta = new_db_meta

    def update_probes(self, *probes: tuple[ShortTableIdentifier, TableProbe]):
        for ti, tp in probes:
            schema_name, table_name = ti
            if schema_name not in self.db_table_probes:
                self.db_table_probes[schema_name] = {}
            self.db_table_probes[schema_name][table_name] = tp

    def drop_probes(self, *to_drop: ShortTableIdentifier):
        for ti in to_drop:
            schema_name, table_name = ti
            if schema_name in self.db_table_probes:
                if table_name in self.db_table_probes[schema_name]:
                    del self.db_table_probes[schema_name][table_name]
