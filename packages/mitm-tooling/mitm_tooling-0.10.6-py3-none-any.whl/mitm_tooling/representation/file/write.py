import pandas as pd

from mitm_tooling.utilities.io_utils import DataSink, FilePath, ensure_directory_exists


def write_header_file(df: pd.DataFrame, sink: DataSink | None) -> str | None:
    """
    Write the `DataFrame` `df` to a CSV file. If `sink` is a `FilePath`, ensure the directory exists.

    :param df: the `DataFrame` to write
    :param sink: a writable byte or text buffer, or a file path
    :return: None, or a string of the CSV-formatted contents if `sink` is None
    """
    if isinstance(sink, FilePath):
        ensure_directory_exists(sink)
    return df.to_csv(sink, header=True, index=False, sep=';')


def write_data_file(df: pd.DataFrame, sink: DataSink | None, append: bool = False) -> str | None:
    """
    Write the `DataFrame` `df` to a CSV file. If `sink` is a `FilePath`, ensure the directory exists.

    :param df: the `DataFrame` to write
    :param sink: a writable byte or text buffer, or a file path
    :param append: whether to include the column header row. It is skipped if `append` is `True`
    :return: None, or a string of the CSV-formatted contents if `sink` is None
    """

    if isinstance(sink, FilePath):
        ensure_directory_exists(sink)
    return df.to_csv(sink, header=not append, index=False, sep=';', date_format='%Y-%m-%dT%H:%M:%S.%f%z')
