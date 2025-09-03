
"""Top-level package API for sushi-train.

This module re-exports selected functions from the submodules so users
can do `import sushi-train` and access the common helpers directly.
"""

from .data_io.duckdb import (
	duckdb_memory_con_init,
	ducklake_init,
	ducklake_attach_minio,
	ducklake_medallion_schema_creation,
	ducklake_refresh,
	update_ducklake_from_minio_parquets,
	update_ducklake_from_minio_csvs,
)
from .data_io.minio import write_data_to_minio_from_parquet_buffer
from .data_io.API import fetch_api_dataframe, fetch_api_paginated_dataframe, add_query_params_to_url, fetch_api_data
from .data_io.azure_blob import (
    get_blob_service_client,
    download_blob_to_bytes,
    upload_bytes_to_blob
)
from .data_io.postgres import get_postgres_engine
from .general.logging import rotating_logger_json
from .transform.SQL import execute_SQL_file_list, execute_SQL_file
from .transform.conversions import (
    convert_dataframe_to_parquet_stream,
    convert_dataframe_to_csv_stream
)

__all__ = [
	"execute_SQL_file_list",
	"execute_SQL_file",
	"add_query_params_to_url",
	"duckdb_memory_con_init",
	"ducklake_init",
	"ducklake_attach_minio",
	"ducklake_medallion_schema_creation",
	"ducklake_refresh",
	"update_ducklake_from_minio_parquets",
	"update_ducklake_from_minio_csvs",
	"write_data_to_minio_from_parquet_buffer",
    "rotating_logger_json",
    "fetch_api_dataframe",
    "fetch_api_paginated_dataframe",
    "convert_dataframe_to_parquet_stream",
    "convert_dataframe_to_csv_stream",
    "fetch_api_data",
    "get_blob_service_client",
    "download_blob_to_bytes",
    "upload_bytes_to_blob",
    "get_postgres_engine"
]
