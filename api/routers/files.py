
from fastapi import APIRouter, UploadFile, File, Depends, Query, Form
from fastapi.responses import Response, JSONResponse

from schemas import (
    FileMetadataOut,
    ListFilesRequest,
    DeleteResponse
)
from services.file_service import (
    upload_file_service,
    list_files_service,
    download_file_service,
    delete_file_service
)
from .auth import get_current_user

router = APIRouter(prefix='/files', tags=['files'])


@router.post('/upload', response_model=FileMetadataOut)
async def upload_file(
    patient_id: str = Form(..., description="Patient ID associated with the file"),
    file: UploadFile = File(..., description="PDF file to upload"),
    user: str = Depends(get_current_user)
):
    """Upload a file for a patient."""
    return await upload_file_service(patient_id, file, user)


@router.get('', response_model=list[FileMetadataOut])
async def list_files(
    patient_id: str = Query(..., description="Patient ID to filter files"),
    user: str = Depends(get_current_user)
):
    """List all files for a patient."""
    return await list_files_service(patient_id)


@router.get('/{file_id}/download')
async def download_file(
    file_id: int,
    user: str = Depends(get_current_user)
):
    """Download a file by ID."""
    content, content_type, filename = await download_file_service(file_id)
    # Encode filename for HTTP header - ensure ASCII-safe
    safe_filename = filename.encode('ascii', 'ignore').decode('ascii')
    if not safe_filename:
        safe_filename = 'file.pdf'
    headers = {
        'Content-Disposition': f'attachment; filename="{safe_filename}"'
    }
    return Response(content=content, media_type=content_type, headers=headers)


@router.delete('/{file_id}', response_model=DeleteResponse)
async def delete_file(
    file_id: int,
    user: str = Depends(get_current_user)
):
    """Delete a file by ID."""
    await delete_file_service(file_id)
    return DeleteResponse(status="deleted")

