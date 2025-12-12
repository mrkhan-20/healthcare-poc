
from fastapi import HTTPException, UploadFile

from io import BytesIO

from dbini import get_db 
from models import FileMetadata
from storage import upload_blob, download_blob_stream, delete_blob, gen_blob_name


async def upload_file_service(
    patient_id: str,
    file: UploadFile,
    uploaded_by: str = None
) -> FileMetadata:
    """Upload a file and store its metadata."""
    # Validate content type
    if file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail='Only PDFs allowed')

    contents = await file.read()
    # Quick magic number check
    if not contents.startswith(b'%PDF'):
        raise HTTPException(status_code=400, detail='Invalid PDF file')

    blob_name = gen_blob_name(file.filename)

    # Upload to blob (use in-memory bytes stream)
    stream = BytesIO(contents)
    await upload_blob(stream, blob_name)

    # Store metadata
    db = next(get_db())
    meta = FileMetadata(
        patient_id=patient_id,
        filename=file.filename,
        content_type=file.content_type,
        size=len(contents),
        blob_name=blob_name,
        uploaded_by=None
    )
    db.add(meta)
    db.commit()
    db.refresh(meta)
    return meta


async def list_files_service(patient_id: str) -> list[FileMetadata]:
    """List all files for a given patient."""
    db = next(get_db())
    rows = db.query(FileMetadata).filter(FileMetadata.patient_id == patient_id).order_by(FileMetadata.uploaded_at.desc()).all()
    return rows


async def get_file_metadata(file_id: int) -> FileMetadata:
    """Get file metadata by ID."""
    db = next(get_db())
    meta = db.query(FileMetadata).filter(FileMetadata.id == file_id).first()
    if not meta:
        raise HTTPException(status_code=404, detail='File not found')
    return meta


async def download_file_service(file_id: int):
    """Download a file by ID."""
    meta = await get_file_metadata(file_id)
    blob_name = meta.blob_name
    content = await download_blob_stream(blob_name)
    return content, meta.content_type, meta.filename


async def delete_file_service(file_id: int):
    """Delete a file by ID."""
    db = next(get_db())
    meta = db.query(FileMetadata).filter(FileMetadata.id == file_id).first()
    if not meta:
        raise HTTPException(status_code=404, detail='File not found')
    await delete_blob(meta.blob_name)
    db.delete(meta)
    db.commit()

