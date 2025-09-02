from abc import ABC, abstractmethod
from datetime import datetime
from enum import IntEnum, StrEnum
from typing import Annotated, Literal, Self
from uuid import UUID

import pydantic
from pydantic import AnyUrl, ConfigDict

from mitm_tooling.data_types import MITMDataType

StrUUID = Annotated[
    UUID,
    pydantic.BeforeValidator(lambda x: UUID(x) if isinstance(x, str) else x),
    pydantic.PlainSerializer(lambda x: str(x)),
    pydantic.Field(description='Better annotation for UUID. Parses from string format, serializes to string format.'),
]

StrUrl = Annotated[
    AnyUrl,
    pydantic.BeforeValidator(lambda x: AnyUrl(x) if isinstance(x, str) else x),
    pydantic.PlainSerializer(lambda x: str(x)),
    pydantic.Field(description='Better annotation for AnyUrl. Parses from string format, serializes to string format.'),
]

StrDatetime = Annotated[
    datetime,
    pydantic.BeforeValidator(lambda x: datetime.fromisoformat(x) if isinstance(x, str) else x),
    pydantic.PlainSerializer(lambda x: str(x)),
    pydantic.Field(
        description='Better annotation for datetime. Parses from string format, serializes to string format.'
    ),
]

SupersetId = int

FilterValue = bool | StrDatetime | float | int | str
FilterValues = FilterValue | list[FilterValue] | tuple[FilterValue]

ColorScheme = Literal['blueToGreen', 'supersetColors']


class GenericDataType(IntEnum):
    NUMERIC = 0
    STRING = 1
    TEMPORAL = 2
    BOOLEAN = 3

    @classmethod
    def from_mitm_dt(cls, dt: MITMDataType) -> Self:
        if dt in {MITMDataType.Numeric, MITMDataType.Integer}:
            return cls.NUMERIC
        elif dt in {MITMDataType.Datetime}:
            return cls.TEMPORAL
        elif dt in {MITMDataType.Boolean}:
            return cls.BOOLEAN
        else:
            return cls.STRING


class AnnotationType(StrEnum):
    Event = 'EVENT'
    Formula = 'FORMULA'
    Interval = 'INTERVAL'
    Timeseries = 'TIME_SERIES'


class AnnotationSource(StrEnum):
    Line = 'line'
    Native = 'NATIVE'
    Table = 'table'
    Undefined = ''


class SupersetVizType(StrEnum):
    PIE = 'pie'
    BIG_NUMBER = 'big_number'
    BIG_NUMBER_TOTAL = 'big_number_total'
    TIMESERIES_BAR = 'echarts_timeseries_bar'
    TIMESERIES_LINE = 'echarts_timeseries_line'
    MAED_CUSTOM = 'maed_custom'
    HORIZON = 'horizon'
    TABLE = 'table'


class ExpressionType(StrEnum):
    SIMPLE = 'SIMPLE'
    SQL = 'SQL'


class SupersetAggregate(StrEnum):
    COUNT = 'COUNT'
    SUM = 'SUM'
    MIN = 'MIN'
    MAX = 'MAX'
    AVG = 'AVG'


class FilterOperator(StrEnum):
    EQUALS = '=='
    NOT_EQUALS = '!='
    GREATER_THAN = '>'
    LESS_THAN = '<'
    GREATER_THAN_OR_EQUALS = '>='
    LESS_THAN_OR_EQUALS = '<='
    LIKE = 'LIKE'
    NOT_LIKE = 'NOT LIKE'
    ILIKE = 'ILIKE'
    IS_NULL = 'IS NULL'
    IS_NOT_NULL = 'IS NOT NULL'
    IN = 'IN'
    NOT_IN = 'NOT IN'
    IS_TRUE = 'IS TRUE'
    IS_FALSE = 'IS FALSE'
    TEMPORAL_RANGE = 'TEMPORAL_RANGE'


class FilterStringOperators(StrEnum):
    EQUALS = 'EQUALS'
    NOT_EQUALS = 'NOT_EQUALS'
    LESS_THAN = 'LESS_THAN'
    GREATER_THAN = 'GREATER_THAN'
    LESS_THAN_OR_EQUAL = 'LESS_THAN_OR_EQUAL'
    GREATER_THAN_OR_EQUAL = 'GREATER_THAN_OR_EQUAL'
    IN = 'IN'
    NOT_IN = 'NOT_IN'
    ILIKE = 'ILIKE'
    LIKE = 'LIKE'
    IS_NOT_NULL = 'IS_NOT_NULL'
    IS_NULL = 'IS_NULL'
    LATEST_PARTITION = 'LATEST_PARTITION'
    IS_TRUE = 'IS_TRUE'
    IS_FALSE = 'IS_FALSE'

    @classmethod
    def from_operator(cls, operator: FilterOperator) -> Self | None:
        try:
            return cls(operator.name)
        except ValueError:
            pass


class TimeGrain(StrEnum):
    SECOND = 'PT1S'
    FIVE_SECONDS = 'PT5S'
    THIRTY_SECONDS = 'PT30S'
    MINUTE = 'PT1M'
    FIVE_MINUTES = 'PT5M'
    TEN_MINUTES = 'PT10M'
    FIFTEEN_MINUTES = 'PT15M'
    THIRTY_MINUTES = 'PT30M'
    HALF_HOUR = 'PT0.5H'
    HOUR = 'PT1H'
    SIX_HOURS = 'PT6H'
    DAY = 'P1D'
    WEEK = 'P1W'
    WEEK_STARTING_SUNDAY = '1969-12-28T00:00:00Z/P1W'
    WEEK_STARTING_MONDAY = '1969-12-29T00:00:00Z/P1W'
    WEEK_ENDING_SATURDAY = 'P1W/1970-01-03T00:00:00Z'
    WEEK_ENDING_SUNDAY = 'P1W/1970-01-04T00:00:00Z'
    MONTH = 'P1M'
    QUARTER = 'P3M'
    QUARTER_YEAR = 'P0.25Y'
    YEAR = 'P1Y'


class ChartDataResultFormat(StrEnum):
    CSV = 'csv'
    JSON = 'json'
    XLSX = 'xlsx'

    @classmethod
    def table_like(cls) -> set[Self]:
        return {cls.CSV, cls.XLSX}


class ChartDataResultType(StrEnum):
    COLUMNS = 'columns'
    FULL = 'full'
    QUERY = 'query'
    RESULTS = 'results'
    SAMPLES = 'samples'
    TIMEGRAINS = 'timegrains'
    POST_PROCESSED = 'post_processed'
    DRILL_DETAIL = 'drill_detail'


class BaseSupersetDefinition(pydantic.BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, use_enum_values=True, validate_by_name=True)


class FrozenSupersetDefinition(BaseSupersetDefinition):
    model_config = ConfigDict(arbitrary_types_allowed=True, use_enum_values=True, validate_by_name=True, frozen=True)


class SupersetDefFile(BaseSupersetDefinition, ABC):
    @property
    @abstractmethod
    def filename(self) -> str:
        pass
