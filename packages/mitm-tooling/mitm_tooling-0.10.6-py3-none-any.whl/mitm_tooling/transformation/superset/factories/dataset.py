from uuid import UUID

import sqlalchemy as sa

from mitm_tooling.data_types import MITMDataType
from mitm_tooling.extraction.relational.data_models import TableMetaInfo
from mitm_tooling.utilities.identifiers import mk_uuid

from ..definitions import SupersetAggregate, SupersetDatasetDef
from .core import mk_column, mk_metric


def mk_dataset(
    tm: TableMetaInfo, database_uuid: UUID, dialect: sa.Dialect | None = None, uuid: UUID | None = None
) -> SupersetDatasetDef:
    cols = []
    metrics = [mk_metric('*', SupersetAggregate.COUNT)]
    main_dttm_col = None
    for c in tm.columns:
        dt = tm.column_properties[c].mitm_data_type
        cols.append(
            mk_column(c, dt, dialect=dialect),
        )
        if dt in {MITMDataType.Numeric}:
            metrics.extend(
                (
                    mk_metric(c, SupersetAggregate.AVG),
                    mk_metric(c, SupersetAggregate.SUM),
                )
            )
        if dt == MITMDataType.Datetime and not main_dttm_col:
            main_dttm_col = dt

    return SupersetDatasetDef(
        table_name=tm.name,
        schema=tm.schema_name,
        uuid=uuid or mk_uuid(),
        database_uuid=database_uuid,
        columns=cols,
        metrics=metrics,
        main_dttm_col=main_dttm_col,
    )
