import io
import polars as pl

def convert_df_to_parquet_buffer(dataframe):
    """
    Convert a Polars DataFrame to an in-memory parquet buffer (io.BytesIO).

    Parameters
    - dataframe: a polars.DataFrame instance

    Returns
    - io.BytesIO containing parquet data on success, or None on failure.
    """
    buffer = io.BytesIO()
    try:
        dataframe.write_parquet(buffer)
        buffer.seek(0)
        result = buffer
        return result
    except Exception as e:
        return None