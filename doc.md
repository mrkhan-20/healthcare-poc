# Technical Design Document — Healthcare Document Manager (Concise)

## 1. Tech Stack & Architecture

1.**Frontend:** React — simple, fast for building upload UI.
2.**Backend:** FastAPI — async, performant, built‑in validation & OpenAPI.
3.**DB:** PostgreSQL — reliable relational store for metadata.
4.**Storage:** Azure Blob Storage — scalable object storage for PDF binaries.
5.**Auth:** JWT (mock).

### Architecture Overview

```
React UI → FastAPI → PostgreSQL (metadata)
                     ↘ Azure Blob Storage (PDF files)
```

The backend handles all validations and never exposes storage credentials. The DB stores only metadata; PDFs reside in blob storage.

---

## 2. Data Flow

### Upload Flow

1. User selects PDF → React sends `multipart/form-data` to backend.
2. FastAPI validates JWT, file type, size, and magic bytes.
3. Backend generates a blob name and uploads binary to Azure Blob.
4. Metadata (filename, size, blob key, patient_id) is stored in Postgres.
5. API returns metadata JSON.

### Download Flow

1. Client requests `GET /files/:id/download`.
2. Backend checks authorization → fetches metadata → streams file from Blob Storage.
3. Client downloads PDF (never sees direct blob path).

**Separation:**

* **Postgres:** only structured metadata.
* **Azure Blob:** raw PDF bytes.

---

## 3. API Specification


### POST /files/upload

**Type:** `multipart/form-data`
**Fields:**

* `patient_id`: string
* `file`: PDF file

**Response:**

```json
{
  "id": 1,
  "patient_id": "p123",
  "filename": "doc.pdf",
  "size": 20480,
  "uploaded_at": "2025-01-01T10:00:00Z"
}
```

### GET /files?patient_id=

Returns list of files for a patient.

### GET /files/:id/download

Streams PDF file to client with proper headers.

### DELETE /files/:id

Deletes metadata + blob.

---

## 4. Key Considerations

### Scalability

* Stateless API; horizontally scalable.
* Blob Storage handles large dataset easily.
* Async I/O supports high upload/download throughput.

### File Storage

* PDFs stored in Azure Blob; DB stores only metadata.
* Blob keys are UUID-based and opaque.

### Error Handling

* Missing file → return 404 or 410.
* Corrupted/mismatched content type → reject upload.
* DB/storage outage → return structured error JSON.

### Security

* JWT-protected APIs.
* Server-side validation of PDFs.
* No direct blob URLs.
* HTTPS required + secrets stored in environment.

---
