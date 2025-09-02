from abc import ABC, abstractmethod

import pandas as pd

from mitm_tooling.utilities.python_utils import recursively_pick_from_mapping


class PandasSeriesTransform(ABC):
    @abstractmethod
    def transform_series(self, s: pd.Series) -> pd.Series:
        pass


class PandasCreation(ABC):
    @abstractmethod
    def make_series(self, df: pd.DataFrame) -> list[pd.Series]:
        pass


class PandasDataframeTransform(ABC):
    @abstractmethod
    def transform_df(self, df: pd.DataFrame) -> pd.DataFrame:
        pass


def extract_json_path(obj, path: tuple[str, ...] | None) -> dict | int | float | str | list | None:
    return recursively_pick_from_mapping(obj, path)


def transform_df(df: pd.DataFrame, transforms: list[PandasDataframeTransform]) -> pd.DataFrame:
    for trans in transforms:
        df = trans.transform_df(df)
    return df
