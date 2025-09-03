import polars as pl

def write_dataframe_to_local_csv(dataframe, file_path):
    try:
        result = dataframe.write_csv(file_path)
        return result
    except Exception as e:
        print(f"Error writing DataFrame to CSV at '{file_path}': {e}")
        raise

def read_local_csv_to_dataframe(file_path):
    try:
        result = pl.read_csv(file_path)
        return result
    except Exception as e:
        print(f"Error reading CSV from '{file_path}': {e}")
        raise

def write_dataframe_to_local_parquet(dataframe, file_path):
    try:
        result = dataframe.write_parquet(file_path)
        return result
    except Exception as e:
        print(f"Error writing DataFrame to Parquet at '{file_path}': {e}")
        raise

def read_local_parquet_to_dataframe(file_path):
    try:
        result = pl.read_parquet(file_path)
        return result
    except Exception as e:
        print(f"Error reading Parquet from '{file_path}': {e}")
        raise

def write_dataframe_to_local_json(dataframe, file_path):
    try:
        result = dataframe.write_json(file_path)
        return result
    except Exception as e:
        print(f"Error writing DataFrame to JSON at '{file_path}': {e}")
        raise

def read_local_json_to_dataframe(file_path):
    try:
        result = pl.read_json(file_path)
        return result
    except Exception as e:
        print(f"Error reading JSON from '{file_path}': {e}")
        raise