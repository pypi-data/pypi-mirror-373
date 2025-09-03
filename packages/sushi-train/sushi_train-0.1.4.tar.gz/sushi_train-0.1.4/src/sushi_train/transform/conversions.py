import io

def convert_dataframe_to_parquet_stream(dataframe):
    buffer = io.BytesIO()
    try:
        dataframe.write_parquet(buffer)
        buffer.seek(0)
        result = buffer
        return result
    except Exception as e:
        print(f"Error in converting dataframe to bytes stream: {e}")
        raise

def convert_dataframe_to_csv_stream(dataframe):
    buffer = io.BytesIO()
    try:
        dataframe.write_csv(buffer)
        buffer.seek(0)
        result = buffer
        return result
    except Exception as e:
        print(f"Error in converting dataframe to bytes stream: {e}")
        raise