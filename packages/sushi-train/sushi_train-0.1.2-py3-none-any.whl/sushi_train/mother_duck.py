import duckdb
import os

def duckdb_memory_con_init():
    """
    Initialize a DuckDB in-memory connection and load required extensions.

    This function installs and loads the `ducklake` and `httpfs` extensions
    then returns a fresh in-memory DuckDB connection.

    Returns
    - con: a duckdb.Connection instance connected to ':memory:'.
    """
    duckdb.install_extension("ducklake")
    duckdb.install_extension("httpfs")
    duckdb.load_extension("ducklake")
    duckdb.load_extension("httpfs")
    con = duckdb.connect(':memory:')
    return con

def ducklake_init(con, data_path, catalog_path):
    """
    Attach and switch to a DuckLake catalog on the given DuckDB connection.

    Parameters
    - con: duckdb connection
    - data_path: path where ducklake will store data
    - catalog_path: path to the ducklake catalog to attach
    """
    con.execute(f"ATTACH 'ducklake:{catalog_path}' AS my_ducklake (DATA_PATH '{data_path}')")
    con.execute("USE my_ducklake")

def ducklake_attach_minio(con, minio_access_key, minio_secret_key, minio_endpoint):
    """
    Configure S3/MinIO credentials and endpoint for DuckDB/DuckLake session.

    Parameters
    - con: duckdb connection
    - minio_access_key: access key id for MinIO
    - minio_secret_key: secret key for MinIO
    - minio_endpoint: endpoint URL or host for MinIO
    """
    con.execute(f"SET s3_access_key_id = '{minio_access_key}'")
    con.execute(f"SET s3_secret_access_key = '{minio_secret_key}'")
    con.execute(f"SET s3_endpoint = '{minio_endpoint}'")
    con.execute("SET s3_use_ssl = false")
    con.execute("SET s3_url_style = 'path'")

def ducklake_medallion_schema_creation(con):
    """
    Create medallion-style schemas (RAW, STAGED, CLEANED) if they do not exist.

    Parameters
    - con: duckdb connection
    """
    con.execute("CREATE SCHEMA IF NOT EXISTS RAW")
    con.execute("CREATE SCHEMA IF NOT EXISTS STAGED")
    con.execute("CREATE SCHEMA IF NOT EXISTS CLEANED")

def ducklake_refresh(con):
    """
    Refresh DuckLake state by expiring snapshots and cleaning up old files.

    Parameters
    - con: duckdb connection
    """
    con.execute("CALL ducklake_expire_snapshots('my_ducklake', older_than => now())")
    con.execute("CALL ducklake_cleanup_old_files('my_ducklake', cleanup_all => true)")


def update_ducklake_from_minio_parquets(con, bucket_name, source_folder_path, target_folder_path):
    """
    Read Parquet files from a MinIO (S3) bucket and create/replace tables in DuckLake.

    Parameters
    - con: duckdb connection
    - bucket_name: name of the S3/MinIO bucket
    - source_folder_path: folder inside the bucket with parquet files
    - target_folder_path: target schema or path in DuckLake where tables are created

    Behavior
    - Uses `glob` to list parquet files in the source path
    - For each parquet file, creates or replaces a table named after the file
      (uppercased, hyphens/spaces replaced with underscores)
    - Adds metadata columns: _source_file, _ingestion_timestamp, _record_id

    Raises
    - Re-raises any exception encountered while listing or creating tables.
    """
    file_list_query = f"SELECT * FROM glob('s3://{bucket_name}/{source_folder_path}/*.parquet')"

    try:
        files_result = con.execute(file_list_query).fetchall()
        file_paths = []
        for row in files_result:
            file_paths.append(row[0])
        
        for file_path in file_paths:
            file_name = os.path.basename(file_path).replace('.parquet', '')
            table_name = file_name.upper().replace('-', '_').replace(' ', '_')

            query = f"""
            CREATE OR REPLACE TABLE {target_folder_path}.{table_name} AS
            SELECT 
                *,
                '{file_name}' AS _source_file,
                CURRENT_TIMESTAMP AS _ingestion_timestamp,
                ROW_NUMBER() OVER () AS _record_id
            FROM read_parquet('{file_path}');
            """
            
            con.execute(query)

    except Exception as e:
        raise


def update_ducklake_from_minio_csvs(con, bucket_name, source_folder_path, target_folder_path):
        """
        Read CSV files from a MinIO (S3) bucket and create/replace tables in DuckLake.

        Parameters
        - con: duckdb connection
        - bucket_name: name of the S3/MinIO bucket
        - source_folder_path: folder inside the bucket with csv files
        - target_folder_path: target schema or path in DuckLake where tables are created
        - csv_options: optional dict of CSV parsing options (passed to read_csv_auto if needed)

        Behavior
        - Uses `glob` to list csv files in the source path
        - For each csv file, creates or replaces a table named after the file
            (uppercased, hyphens/spaces replaced with underscores)
        - Adds metadata columns: _source_file, _ingestion_timestamp, _record_id

        Notes
        - This uses DuckDB's `read_csv_auto` to infer schema; if you require explicit
            options (delimiter, header, etc.) pass `csv_options` as a dict and use
            alternative read approaches as needed.

        Raises
        - Re-raises any exception encountered while listing or creating tables.
        """
        file_list_query = f"SELECT * FROM glob('s3://{bucket_name}/{source_folder_path}/*.csv')"

        try:
                files_result = con.execute(file_list_query).fetchall()
                file_paths = []
                for row in files_result:
                        file_paths.append(row[0])

                for file_path in file_paths:
                        file_name = os.path.basename(file_path).replace('.csv', '')
                        table_name = file_name.upper().replace('-', '_').replace(' ', '_')

                        query = f"""
                        CREATE OR REPLACE TABLE {target_folder_path}.{table_name} AS
                        SELECT
                                *,
                                '{file_name}' AS _source_file,
                                CURRENT_TIMESTAMP AS _ingestion_timestamp,
                                ROW_NUMBER() OVER () AS _record_id
                        FROM read_csv_auto('{file_path}');
                        """

                        con.execute(query)

        except Exception as e:
                raise