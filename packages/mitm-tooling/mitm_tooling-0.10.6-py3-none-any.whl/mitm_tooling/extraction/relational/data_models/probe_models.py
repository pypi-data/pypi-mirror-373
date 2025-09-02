from datetime import datetime
from typing import Annotated

import numpy as np
import pandas as pd
import pydantic
from pydantic import Field, NonNegativeInt

FloatPercentage = Annotated[float, Field(ge=0.0, le=1.0)]
SanitizedAny = Annotated[str, pydantic.BeforeValidator(lambda v: str(v)), pydantic.PlainSerializer(lambda v: str(v))]


class NumericSummaryStatistics(pydantic.BaseModel):
    count: int
    mean: float
    min: float
    max: float
    std: float | None = None
    percentile_25: float
    percentile_50: float
    percentile_75: float

    @staticmethod
    def empty():
        return NumericSummaryStatistics(
            count=0,
            mean=np.nan,
            min=np.nan,
            max=np.nan,
            std=np.nan,
            percentile_25=np.nan,
            percentile_50=np.nan,
            percentile_75=np.nan,
        )


class DatetimeSummaryStatistics(pydantic.BaseModel):
    count: int
    mean: datetime | None = None
    min: datetime | None = None
    max: datetime | None = None
    # std: datetime
    percentile_25: datetime | None = None
    percentile_50: datetime | None = None
    percentile_75: datetime | None = None

    @staticmethod
    def empty():
        return DatetimeSummaryStatistics(count=0)


class CategoricalSummaryStatistics(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    count: NonNegativeInt
    unique: NonNegativeInt
    top: SanitizedAny
    freq: NonNegativeInt

    @staticmethod
    def empty():
        return CategoricalSummaryStatistics(count=0, unique=0, top=pd.NA, freq=0)


class SampleSummary(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    sample_size: NonNegativeInt | None = None
    na_fraction: FloatPercentage | None = None
    unique_fraction: FloatPercentage | None = None
    value_counts: dict[SanitizedAny, int] | None = None
    summary_statistics: NumericSummaryStatistics | CategoricalSummaryStatistics | DatetimeSummaryStatistics | None = (
        None
    )
    json_schema: dict | None = None
