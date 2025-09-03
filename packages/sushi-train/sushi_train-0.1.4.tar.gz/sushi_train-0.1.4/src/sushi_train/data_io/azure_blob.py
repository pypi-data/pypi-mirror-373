import io
from azure.storage.blob import BlobServiceClient

def get_blob_service_client(connection_string):
    if not connection_string:
        raise ValueError("Connection string incorrect or missing.")
    try:
        client = BlobServiceClient.from_connection_string(connection_string)
        return client
    except Exception as e:
        print(f"Error creating BlobServiceClient: {e}")
        raise
    
def download_blob_to_bytes(blob_service_client, container_name, filename):
    try:
        blob_client = blob_service_client.get_blob_client(
        container=container_name, blob=filename
    )
        blob_data = blob_client.download_blob().readall()
        file_in_memory = io.BytesIO(blob_data)
        return file_in_memory
    except Exception as e:
        print(f"Error downloading blob to bytes: {e}")
        raise


def upload_bytes_to_blob(blob_service_client, container_name, filename, data):
    try:
        blob_client = blob_service_client.get_blob_client(
            container=container_name, blob=filename
        )
        blob_client.upload_blob(data, overwrite=True)
    except Exception as e:
        print(f"Error uploading bytes to blob: {e}")
        raise