import io


def write_data_to_minio_from_parquet_buffer(parquet_buffer, minio_client, bucket_name, object_name, folder_name=None):    
    """
    Upload a parquet binary buffer to MinIO as an object.

    Parameters
    - parquet_buffer: io.BytesIO containing parquet bytes (will be seeked to 0)
    - minio_client: an instantiated MinIO client with put_object method
    - bucket_name: target bucket name
    - object_name: desired object name (filename)
    - folder_name: optional folder inside bucket to place the object

    Raises
    - Re-raises any exception from the MinIO client.
    """
    parquet_buffer.seek(0)
    data_bytes = parquet_buffer.read()

    if folder_name:
        folder_name = folder_name.strip("/")
        full_object_name = f"{folder_name}/{object_name}"
    else:
        full_object_name = object_name

    try:
        minio_client.put_object(
            bucket_name,
            full_object_name,
            io.BytesIO(data_bytes),
            length=len(data_bytes),
            content_type="application/x-parquet",
        )
    except Exception as e:
        raise