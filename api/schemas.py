from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# Auth Request Schemas
class LoginRequest(BaseModel):
    """Request schema for user login."""
    username: str = Field(..., description="Username for authentication")


# File Request Schemas
class FileUploadRequest(BaseModel):
    """Request schema for file upload (patient_id as form field)."""
    patient_id: str = Field(..., description="Patient ID associated with the file")


class ListFilesRequest(BaseModel):
    """Request schema for listing files (query parameters)."""
    patient_id: str = Field(..., description="Patient ID to filter files")


class FileDownloadRequest(BaseModel):
    """Request schema for file download (path parameter)."""
    file_id: int = Field(..., description="File ID to download", gt=0)


class FileDeleteRequest(BaseModel):
    """Request schema for file deletion (path parameter)."""
    file_id: int = Field(..., description="File ID to delete", gt=0)


# Response Schemas
class LoginResponse(BaseModel):
    """Response schema for login."""
    access_token: str = Field(..., description="JWT access token")


class FileCreateResponse(BaseModel):
    """Response schema for file creation."""
    id: int
    filename: str
    patient_id: str
    size: int
    uploaded_at: datetime


class FileMetadataOut(BaseModel):
    """Response schema for file metadata."""
    id: int
    patient_id: str
    filename: str
    size: int
    uploaded_at: datetime

    class Config:
        orm_mode = True


class DeleteResponse(BaseModel):
    """Response schema for file deletion."""
    status: str = Field(default="deleted", description="Deletion status")
    message: Optional[str] = Field(default=None, description="Optional message")
