from typing import Annotated, Any, Literal

import pydantic
from pydantic import SerializeAsAny

from mitm_tooling.utilities.identifiers import name_plus_uuid

from .constants import ColorScheme, StrUrl, StrUUID, SupersetDefFile, SupersetVizType
from .core import (
    AnnotationLayer,
    ColumnName,
    DatasetIdentifier,
    FormData,
    QueryContext,
    SupersetAdhocFilter,
    SupersetAdhocMetric,
    SupersetId,
    SupersetObjectMixin,
    TimeGrain,
)
from .identifiers import ChartIdentifier


class BaseChartParams(FormData):
    datasource: str | DatasetIdentifier
    viz_type: SupersetVizType
    groupby: list[str] = pydantic.Field(default_factory=list)
    adhoc_filters: list[SupersetAdhocFilter] = pydantic.Field(default_factory=list)
    row_limit: int = 10000
    extra_form_data: dict[str, Any] = pydantic.Field(default_factory=dict)
    slice_id: SupersetId | None = None
    dashboards: list[SupersetId] = pydantic.Field(default_factory=list)


class ChartParams(BaseChartParams):
    sort_by_metric: bool = True
    color_scheme: ColorScheme = 'supersetColors'
    show_legend: bool = True
    legendType: str = 'scroll'
    legendOrientation: str = 'top'


class PieChartParams(ChartParams):
    viz_type: Literal[SupersetVizType.PIE] = SupersetVizType.PIE
    metric: SupersetAdhocMetric
    show_labels_threshold: int = 5
    show_labels: bool = True
    labels_outside: bool = True
    outerRadius: int = 70
    innerRadius: int = 30
    label_type: str = 'key'
    number_format: str = 'SMART_NUMBER'
    date_format: str = 'smart_date'


class BigNumberTotalChartParams(ChartParams):
    viz_type: Literal[SupersetVizType.BIG_NUMBER_TOTAL] = SupersetVizType.BIG_NUMBER_TOTAL
    metric: str | SupersetAdhocMetric
    header_font_size: float = 0.4
    subtitle_font_size: float = 0.15
    y_axis_format: str = 'SMART_NUMBER'
    time_format: str = 'smart_date'


BigNumberAggregation = Literal['sum', 'mean', 'min', 'max', 'last']


class BigNumberChartParams(BigNumberTotalChartParams):
    viz_type: Literal[SupersetVizType.BIG_NUMBER] = SupersetVizType.BIG_NUMBER
    x_axis: ColumnName
    time_grain_sqla: TimeGrain | None = None
    aggregation: BigNumberAggregation = 'sum'
    compare_lag: int | None = None
    compare_suffix: str | None = None
    show_timestamp: bool = True
    show_trend_line: bool = True
    start_y_axis_at_zero: bool = True
    subheader_font_size: float = 0.15
    rolling_type: str | None = None


class TimeSeriesChartParams(ChartParams):
    metrics: list[str | SupersetAdhocMetric]
    x_axis: ColumnName
    x_axis_sort_asc: bool = True
    x_axis_sort_series: str = 'name'
    x_axis_sort_series_ascending: bool = True
    x_axis_time_format: str = 'smart_date'
    x_axis_title_margin: int = 15
    y_axis_format: str = 'SMART_NUMBER'
    y_axis_bounds: tuple[float | None, float | None] = (None, None)
    y_axis_title_margin: int = 15
    y_axis_title_position: str = 'Left'
    truncateXAxis: bool = True
    truncate_metric: bool = True
    show_empty_columns: bool = True
    comparison_type: str = 'values'
    rich_tooltip: bool = True
    showTooltipTotal: bool = True
    showTooltipPercentage: bool = True
    tooltipTimeFormat: str = 'smart_date'
    sort_series_type: str = 'sum'
    orientation: str = 'vertical'
    only_total: bool = True
    order_desc: bool = True
    time_grain_sqla: TimeGrain | None = None
    annotation_layers: list[AnnotationLayer] | None = pydantic.Field(default_factory=list)

    #
    # forecastEnabled: bool = False
    # forecastPeriods: int = 10
    # forecastInterval: float = 0.8


class TimeSeriesBarParams(TimeSeriesChartParams):
    viz_type: Literal[SupersetVizType.TIMESERIES_BAR] = SupersetVizType.TIMESERIES_BAR


class TimeSeriesLineParams(TimeSeriesChartParams):
    viz_type: Literal[SupersetVizType.TIMESERIES_LINE] = SupersetVizType.TIMESERIES_LINE
    opacity: float = 0.2
    markerSize: int = 6
    seriesType: str = 'line'


class HorizonChartParams(BaseChartParams):
    viz_type: Literal[SupersetVizType.HORIZON] = SupersetVizType.HORIZON
    metrics: list[str | SupersetAdhocMetric]
    horizon_color_scale: str = 'series'
    contribution: bool = False
    order_desc: bool = True
    series_height: int = 25
    granularity_sqla: ColumnName | None = None  # for some reason misused in the chart for time column name (I believe)
    time_range: str = 'No Filter'


class TableChartParams(BaseChartParams):
    viz_type: Literal[SupersetVizType.TABLE] = SupersetVizType.TABLE
    query_mode: Literal['raw', 'aggregate'] = 'raw'
    all_columns: list[ColumnName] = pydantic.Field(default_factory=list)
    metrics: list[str | SupersetAdhocMetric] | None = None
    percent_metrics: list[str | SupersetAdhocMetric] = pydantic.Field(default_factory=list)
    order_by_cols: list[str] = pydantic.Field(default_factory=list)
    time_grain_sqla: TimeGrain | None = None
    temporal_columns_lookup: dict | None = None
    server_page_length: int = 10
    table_timestamp_format: str = 'smart_date'
    allow_render_html: bool = True
    show_cell_bars: bool = True
    color_pn: bool = True
    comparison_color_scheme: str = 'Green'
    comparison_type: str = 'values'


# has been replaced by simple str
JsonQueryContext = Annotated[
    QueryContext,
    pydantic.PlainSerializer(
        lambda x: x.model_dump_json(by_alias=True, exclude_none=True, warnings=False)
        if isinstance(x, pydantic.BaseModel)
        else x,
        return_type=pydantic.Json,
    ),
    pydantic.BeforeValidator(lambda x: QueryContext.model_validate(**x) if isinstance(x, dict) else x),
]


class SupersetChartDef(SupersetObjectMixin, SupersetDefFile):
    uuid: StrUUID
    slice_name: str
    viz_type: SupersetVizType
    dataset_uuid: StrUUID
    description: str | None = None
    certified_by: str | None = None
    certification_details: str | None = None
    params: SerializeAsAny[BaseChartParams | None] = None
    query_context: str | None = None

    cache_timeout: int | None = None
    version: str = '1.0.0'
    is_managed_externally: bool = False
    external_url: StrUrl | None = None

    @property
    def filename(self) -> str:
        return name_plus_uuid(self.slice_name, self.uuid, sep='_')

    @property
    def identifier(self) -> ChartIdentifier:
        return ChartIdentifier(uuid=self.uuid, slice_name=self.slice_name, id=-1)
