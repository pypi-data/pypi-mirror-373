from typing import Literal
from uuid import UUID

from ..definitions import ChartParams, DatasetIdentifier, MitMDatasetIdentifier, SupersetChartDef, SupersetVizType
from .chart import mk_chart_def
from .query import mk_query_context, mk_query_object


class MAEDCustomChartParams(ChartParams):
    viz_type: Literal[SupersetVizType.MAED_CUSTOM] = SupersetVizType.MAED_CUSTOM
    mitm_dataset: MitMDatasetIdentifier


def mk_maed_custom_chart(
    name: str,
    mitm_dataset_identifier: MitMDatasetIdentifier,
    datasource_identifier: DatasetIdentifier,
    uuid: UUID | None = None,
    **kwargs,
) -> SupersetChartDef:
    params = MAEDCustomChartParams(datasource=datasource_identifier, mitm_dataset=mitm_dataset_identifier)
    qo = mk_query_object()
    qc = mk_query_context(datasource=datasource_identifier, queries=[qo], form_data=params)

    return mk_chart_def(
        name,
        dataset_uuid=datasource_identifier.uuid,
        viz_type=SupersetVizType.MAED_CUSTOM,
        params=params,
        query_context=qc,
        uuid=uuid,
        **kwargs,
    )
