from collections.abc import Generator

import pandas as pd


def chunk_df(df: pd.DataFrame, chunk_size: int | None = 100_000) -> Generator[pd.DataFrame, None, None]:
    if chunk_size is None:
        yield df
    else:
        L = len(df)
        num_chunks = int(L / chunk_size)
        for i in range(0, num_chunks):
            yield df.iloc[i * chunk_size : (i + 1) * chunk_size]
        # last, possibly smaller chunk
        if num_chunks * chunk_size < L:
            yield df.iloc[num_chunks * chunk_size :]
