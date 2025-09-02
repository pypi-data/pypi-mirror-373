from enum import StrEnum
from typing import Annotated, Literal

import pydantic
from pydantic import SerializeAsAny

from mitm_tooling.utilities.identifiers import name_plus_uuid

from .constants import StrUrl, StrUUID, SupersetDefFile, SupersetId
from .core import SupersetObjectMixin
from .identifiers import DashboardIdentifier

DashboardInternalID = str


class DashboardComponentType(StrEnum):
    CHART = 'CHART'
    HEADER = 'HEADER'
    GRID = 'GRID'
    ROOT = 'ROOT'
    ROW = 'ROW'
    COLUMN = 'COLUMN'
    TAB = 'TAB'
    TABS = 'TABS'
    MARKDOWN = 'MARKDOWN'
    DIVIDER = 'DIVIDER'


BackgroundType = Literal['BACKGROUND_TRANSPARENT', 'BACKGROUND_WHITE']
HeaderSize = Literal['SMALL_HEADER', 'MEDIUM_HEADER', 'LARGE_HEADER']


class ComponentMeta(pydantic.BaseModel):
    pass


DuckTypedOptionalComponentMeta = Annotated[
    ComponentMeta | None, pydantic.SerializeAsAny(), pydantic.Field(default=None)
]


class DashboardComponent(pydantic.BaseModel):
    id: DashboardInternalID
    type: DashboardComponentType
    meta: SerializeAsAny[ComponentMeta | None] = pydantic.Field(default=None)
    children: list[DashboardInternalID] = pydantic.Field(default_factory=list)


class HeaderMeta(ComponentMeta):
    text: str
    background: BackgroundType | None = None
    headerSize: HeaderSize | None = None


class DashboardHeader(DashboardComponent):
    type: Literal[DashboardComponentType.HEADER] = DashboardComponentType.HEADER
    meta: HeaderMeta


class DashboardRoot(DashboardComponent):
    type: Literal[DashboardComponentType.ROOT] = DashboardComponentType.ROOT
    meta: None = None


class DashboardGrid(DashboardComponent):
    type: Literal[DashboardComponentType.GRID] = DashboardComponentType.GRID
    meta: None = None


class RowMeta(ComponentMeta):
    background: BackgroundType = 'BACKGROUND_TRANSPARENT'


class DashboardRow(DashboardComponent):
    type: Literal[DashboardComponentType.ROW] = DashboardComponentType.ROW
    meta: RowMeta = pydantic.Field(default_factory=RowMeta)


class ColumnMeta(RowMeta):
    width: int = pydantic.Field(ge=0, le=12, default=3)


class DashboardColumn(DashboardComponent):
    type: Literal[DashboardComponentType.COLUMN] = DashboardComponentType.COLUMN
    meta: ColumnMeta = pydantic.Field(default_factory=ColumnMeta)


class MarkdownMeta(ComponentMeta):
    height: int = pydantic.Field(ge=0, default=50)
    width: int = pydantic.Field(ge=0, le=12, default=4)
    code: str | None = None


class DashboardMarkdown(DashboardComponent):
    type: Literal[DashboardComponentType.MARKDOWN] = DashboardComponentType.MARKDOWN
    meta: MarkdownMeta = pydantic.Field(default_factory=MarkdownMeta)


class DashboardDivider(DashboardComponent):
    type: Literal[DashboardComponentType.DIVIDER] = DashboardComponentType.DIVIDER


class TabMeta(ComponentMeta):
    text: str = ''
    defaultText: str | None = None
    placeholder: str | None = None


class DashboardTab(DashboardComponent):
    type: Literal[DashboardComponentType.TAB] = DashboardComponentType.TAB
    meta: TabMeta = pydantic.Field(default_factory=TabMeta)


class DashboardTabs(DashboardComponent):
    type: Literal[DashboardComponentType.TABS] = DashboardComponentType.TABS


class ChartMeta(ComponentMeta):
    uuid: StrUUID
    width: int = pydantic.Field(ge=1, le=12)
    height: int
    chartId: SupersetId = (
        -1
    )  # Placeholder value just so the key exists. Alternatively, use .model_dump(exclude_none=False)
    sliceName: str | None = None


class DashboardChart(DashboardComponent):
    type: Literal[DashboardComponentType.CHART] = DashboardComponentType.CHART
    meta: ChartMeta


DASHBOARD_VERSION_KEY_LITERAL = Literal['DASHBOARD_VERSION_KEY']

DashboardPositionData = dict[DASHBOARD_VERSION_KEY_LITERAL | DashboardInternalID, str | DashboardComponent]


class ControlValues(pydantic.BaseModel):
    enableEmptyFilter: bool = False
    defaultToFirstItem: bool | None = None
    multiSelect: bool | None = None
    searchAllOptions: bool | None = None
    inverseSelection: bool | None = None


class ColName(pydantic.BaseModel):
    name: str


class DatasetReference(pydantic.BaseModel):
    datasetUuid: StrUUID


class ColumnOfDataset(DatasetReference):
    column: ColName


class FilterType(StrEnum):
    FILTER_SELECT = 'filter_select'
    FILTER_TIME_GRAIN = 'filter_timegrain'
    FILTER_TIME = 'filter_time'


class NativeFilterScope(pydantic.BaseModel):
    rootPath: list[str] = pydantic.Field(default_factory=lambda: ['ROOT_ID'])
    excluded: list[str] = pydantic.Field(default_factory=list)


class NativeFilterConfig(pydantic.BaseModel):
    id: str
    name: str
    targets: list[DatasetReference | ColumnOfDataset | dict] = pydantic.Field(default_factory=lambda: [{}])
    controlValues: ControlValues = pydantic.Field(default_factory=ControlValues)
    filterType: FilterType = FilterType.FILTER_SELECT
    type: str = 'NATIVE_FILTER'
    scope: NativeFilterScope = pydantic.Field(default_factory=NativeFilterScope)


class DashboardMetadata(pydantic.BaseModel):
    color_scheme: str = 'blueToGreen'
    cross_filters_enabled: bool = True
    native_filter_configuration: list[NativeFilterConfig] = pydantic.Field(default_factory=list)
    chart_configuration: dict = pydantic.Field(default_factory=dict)
    global_chart_configuration: dict = pydantic.Field(default_factory=dict)
    default_filters: str | None = None
    filter_scopes: dict = pydantic.Field(default_factory=dict)
    expanded_slices: dict = pydantic.Field(default_factory=dict)


class SupersetDashboardDef(SupersetObjectMixin, SupersetDefFile):
    uuid: StrUUID
    dashboard_title: str
    position: DashboardPositionData
    metadata: DashboardMetadata
    description: str | None = None
    css: str | None = None
    slug: str | None = None
    is_managed_externally: bool | None = False
    external_url: StrUrl | None = None
    certified_by: str | None = None
    certification_details: str | None = None
    published: bool | None = False
    version: str = '1.0.0'

    @property
    def filename(self) -> str:
        return name_plus_uuid(self.dashboard_title, self.uuid, sep='_')

    @property
    def identifier(self) -> DashboardIdentifier:
        return DashboardIdentifier(uuid=self.uuid, dashboard_title=self.dashboard_title, id=-1)
