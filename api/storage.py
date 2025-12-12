import os
from azure.storage.blob.aio import BlobServiceClient
from azure.core.exceptions import ResourceExistsError
import uuid
from dotenv import load_dotenv
from io import BytesIO

load_dotenv()

AZ_CONN = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
CONTAINER = os.getenv('BLOB_CONTAINER', 'health-docs')


def _get_blob_service_client():
    """Create a new BlobServiceClient instance."""
    return BlobServiceClient.from_connection_string(AZ_CONN)


async def ensure_container():
    """Ensure the blob container exists."""
    async with _get_blob_service_client() as blob_svc:
        container_client = blob_svc.get_container_client(CONTAINER)
        try:
            await container_client.create_container()
        except ResourceExistsError:
            pass


async def upload_blob(file_stream, blob_name: str):
    """Upload a blob to Azure Storage."""
    async with _get_blob_service_client() as blob_svc:
        container_client = blob_svc.get_container_client(CONTAINER)
        blob_client = container_client.get_blob_client(blob_name)
        await blob_client.upload_blob(
            file_stream,
            overwrite=True,
        )
    return blob_name


async def download_blob_stream(blob_name: str):
    """Download a blob stream from Azure Storage."""
    async with _get_blob_service_client() as blob_svc:
        container_client = blob_svc.get_container_client(CONTAINER)
        blob_client = container_client.get_blob_client(blob_name)
        stream = await blob_client.download_blob()
        # Read the stream content before closing the client
        content = await stream.readall()
        return content


async def delete_blob(blob_name: str):
    """Delete a blob from Azure Storage."""
    async with _get_blob_service_client() as blob_svc:
        container_client = blob_svc.get_container_client(CONTAINER)
        blob_client = container_client.get_blob_client(blob_name)
        await blob_client.delete_blob()


def gen_blob_name(filename: str) -> str:
    """Generate a unique blob name from filename."""
    # keep original extension, add uuid prefix
    ext = filename.split('.')[-1]
    return f"{uuid.uuid4().hex}.{ext}"