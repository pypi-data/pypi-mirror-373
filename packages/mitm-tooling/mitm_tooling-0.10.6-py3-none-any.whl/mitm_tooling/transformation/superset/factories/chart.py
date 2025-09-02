from uuid import UUID

from mitm_tooling.utilities.identifiers import mk_uuid

from ..definitions import BaseChartParams, QueryContext, SupersetChartDef, SupersetVizType


def mk_chart_def(
    name: str,
    dataset_uuid: UUID,
    viz_type: SupersetVizType,
    params: BaseChartParams,
    query_context: QueryContext,
    uuid: UUID | None = None,
    **kwargs,
) -> SupersetChartDef:
    return SupersetChartDef(
        slice_name=name,
        viz_type=viz_type,
        dataset_uuid=dataset_uuid,
        params=params,
        query_context=query_context.model_dump_json(exclude_none=True, by_alias=True, warnings=False),
        uuid=uuid or mk_uuid(),
        **kwargs,
    )
