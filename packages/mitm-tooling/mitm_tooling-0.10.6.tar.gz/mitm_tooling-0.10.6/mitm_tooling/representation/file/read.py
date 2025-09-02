import pandas as pd

from mitm_tooling.data_types.convert import convert_df
from mitm_tooling.definition import MITM, ConceptName
from mitm_tooling.utilities.io_utils import DataSource, use_for_pandas_io

from ..common import guess_k_of_header_df, mk_concept_file_header, mk_header_file_columns


def read_header_file(source: DataSource, normalize: bool = False) -> pd.DataFrame:
    """
    Read a CSV file into a `DataFrame`, optionally reindexing the columns as expected
    in the intermediate representation of a header file.

    :param source: a readable byte or text buffer, or a file path
    :param normalize: whether to reindex the columns as expected in the intermediate representation
    :return: the read `DataFrame`
    """

    with use_for_pandas_io(source) as f:
        df = pd.read_csv(f, sep=';')
        if normalize:
            k = guess_k_of_header_df(df)
            df = df.astype(pd.StringDtype()).reindex(columns=mk_header_file_columns(k))
        return df


def read_data_file(
    source: DataSource,
    target_mitm: MITM | None = None,
    target_concept: ConceptName | None = None,
    normalize: bool = False,
) -> pd.DataFrame:
    """
    Read a CSV file into a `DataFrame`, optionally reindexing the columns as expected
    in the intermediate representation given the `target_concept` of the `target_mitm`.

    :param source: a readable byte or text buffer, or a file path
    :param target_mitm: the target MITM
    :param target_concept: the target concept
    :param normalize: whether to reindex the columns as expected in the intermediate representation
    :return: the read `DataFrame`
    """

    with use_for_pandas_io(source) as f:
        df = pd.read_csv(f, sep=';', date_format='%Y-%m-%dT%H:%M:%S.%f%z', low_memory=False)
        if normalize and target_mitm and target_concept:
            k = guess_k_of_header_df(df)
            cols, column_dts = mk_concept_file_header(target_mitm, target_concept, k)
            df = df.reindex(columns=cols)
            convert_df(df, column_dts, inplace=True)
        return df
