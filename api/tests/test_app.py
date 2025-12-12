# test_app.py
import sys
import os
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock database before importing main to prevent production DB connection
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

# Set up test database first
TEST_DB_URL = "sqlite:///./test.db"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Mock the db module before importing main
import db
db.engine = test_engine  # Replace production engine with test engine
db.SessionLocal = TestingSessionLocal  # Replace production session maker with test one

# Now import main (it will use the mocked engine)
from fastapi.testclient import TestClient
from main import app
from services.auth_service import create_access_token
from db import Base
from dbini import get_db
from models import FileMetadata

# Create tables with test engine
Base.metadata.create_all(bind=test_engine)

def override_get_db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# ----------------------------
# Mock Azure Blob Storage
# ----------------------------
@pytest.fixture(autouse=True)
def mock_blob(monkeypatch):
    async def dummy_upload(*args, **kwargs): return True
    async def dummy_delete(*args, **kwargs): return True
    async def dummy_download(*args, **kwargs):
        return b"%PDF mock file"
    async def dummy_ensure_container(*args, **kwargs): return None

    # Patch where the functions are used (in services.file_service)
    monkeypatch.setattr("services.file_service.upload_blob", dummy_upload)
    monkeypatch.setattr("services.file_service.delete_blob", dummy_delete)
    monkeypatch.setattr("services.file_service.download_blob_stream", dummy_download)
    # Also patch in storage module for ensure_container
    monkeypatch.setattr("storage.ensure_container", dummy_ensure_container)
    yield

# ----------------------------
# Auth Header Fixture
# ----------------------------
@pytest.fixture
def auth_header():
    token = create_access_token("tester")
    return {"Authorization": f"Bearer {token}"}

# -----------------------------------------------------
# Test: Reject non-PDF files
# -----------------------------------------------------
def test_reject_non_pdf(auth_header):
    res = client.post(
        "/files/upload",
        files={"file": ("bad.txt", b"not pdf", "text/plain")},
        data={"patient_id": "p1"},
        headers=auth_header
    )
    assert res.status_code == 400

# -----------------------------------------------------
# Test: Metadata stored after valid upload
# -----------------------------------------------------
def test_metadata_stored(auth_header):
    pdf = b"%PDF-1.4 test-file"
    res = client.post(
        "/files/upload",
        files={"file": ("report.pdf", pdf, "application/pdf")},
        data={"patient_id": "p1"},
        headers=auth_header
    )

    assert res.status_code == 200
    doc_id = res.json()["id"]

    session = TestingSessionLocal()
    record = session.get(FileMetadata, doc_id)
    assert record is not None
    assert record.filename == "report.pdf"
    session.close()

# -----------------------------------------------------
# Test: Download requires auth
# -----------------------------------------------------
def test_download_requires_auth():
    res = client.get("/files/1/download")
    assert res.status_code == 401
