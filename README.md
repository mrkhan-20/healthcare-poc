# Healthcare Document Manager

![Project Image](ui/public/image.png)

A healthcare document management system built with React frontend and FastAPI backend, using PostgreSQL for metadata storage and Azure Blob Storage for PDF file storage.

## Assumptions

Based on the technical design document, the following assumptions have been made:

1. **Authentication**: JWT-based authentication is implemented as a mock system for PoC purposes. Any username is accepted for login.
2. **File Storage**: PDF files are stored in Azure Blob Storage, while only metadata (filename, size, patient_id, blob key, upload timestamp) is stored in PostgreSQL.
3. **File Validation**: Server-side validation ensures only PDF files are accepted, including magic byte verification.
4. **Security**: All API endpoints require JWT authentication. Storage credentials are never exposed to clients.
5. **Architecture**: The system uses a stateless API design that is horizontally scalable. Async I/O supports high upload/download throughput.
6. **Error Handling**: Structured error responses are returned for missing files (404/410), corrupted content, and database/storage outages.
7. **CORS**: The API allows requests from `http://localhost:3000` for development purposes.

## Setup Instructions

### Prerequisites

- Docker and Docker Compose installed
- Azure Storage Account with Blob Storage (for production)
- Python 3.8+ (for local development)
- Node.js 14+ (for local UI development)

### Using Docker Compose (Recommended)

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd healthcare-poc
   ```

2. **Set up environment variables**:
   
   Create a `.env` file in the root directory (optional, defaults are provided):
   ```env
   AZURE_STORAGE_CONNECTION_STRING=your_azure_connection_string
   BLOB_CONTAINER=health-docs
   ```

3. **Start the services**:
   ```bash
   docker-compose up -d
   ```

   This will start:
   - PostgreSQL database on port `5432`
   - FastAPI backend on port `8000`
   - React frontend on port `3000`

4. **Access the application**:
   - Frontend UI: http://localhost:3000
   - API Documentation: http://localhost:8000/docs
   - API Alternative Docs: http://localhost:8000/redoc

### Local Development Setup

#### Backend Setup

1. **Navigate to the API directory**:
   ```bash
   cd api
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   
   Create a `.env` file in the `api` directory:
   ```env
   DATABASE_URL=postgresql://postgres:1234@localhost:5432/health-docs
   AZURE_STORAGE_CONNECTION_STRING=your_azure_connection_string
   BLOB_CONTAINER=health-docs
   ```

5. **Start PostgreSQL** (if not using Docker):
   ```bash
   docker-compose up -d db
   ```

6. **Run the API server**:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

#### Frontend Setup

1. **Navigate to the UI directory**:
   ```bash
   cd ui
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm start
   ```

   The UI will be available at http://localhost:3000

## API Usage Examples

### Authentication

#### Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### File Operations

All file operations require authentication. Include the JWT token in the Authorization header.

#### Upload a File
```bash
curl -X POST "http://localhost:8000/files/upload" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "patient_id=p123" \
  -F "file=@/path/to/your/document.pdf"
```

**Response:**
```json
{
  "id": 1,
  "patient_id": "p123",
  "filename": "document.pdf",
  "size": 20480,
  "uploaded_at": "2025-01-01T10:00:00Z"
}
```

#### List Files for a Patient
```bash
curl -X GET "http://localhost:8000/files?patient_id=p123" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
[
  {
    "id": 1,
    "patient_id": "p123",
    "filename": "document.pdf",
    "size": 20480,
    "uploaded_at": "2025-01-01T10:00:00Z"
  }
]
```

#### Download a File
```bash
curl -X GET "http://localhost:8000/files/1/download" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -o downloaded_file.pdf
```

#### Delete a File
```bash
curl -X DELETE "http://localhost:8000/files/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
{
  "status": "deleted"
}
```

### Complete Workflow Example

```bash
# 1. Login and save token
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser"}' | jq -r '.access_token')

# 2. Upload a file
curl -X POST "http://localhost:8000/files/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "patient_id=p123" \
  -F "file=@document.pdf"

# 3. List files
curl -X GET "http://localhost:8000/files?patient_id=p123" \
  -H "Authorization: Bearer $TOKEN"

# 4. Download a file (replace 1 with actual file ID)
curl -X GET "http://localhost:8000/files/1/download" \
  -H "Authorization: Bearer $TOKEN" \
  -o downloaded.pdf

# 5. Delete a file
curl -X DELETE "http://localhost:8000/files/1" \
  -H "Authorization: Bearer $TOKEN"
```

## Project Structure

```
healthcare-poc/
├── api/                 # FastAPI backend
│   ├── routers/        # API route handlers
│   ├── services/       # Business logic
│   ├── models.py       # Database models
│   ├── schemas.py      # Pydantic schemas
│   └── main.py         # FastAPI application
├── ui/                 # React frontend
│   ├── src/           # React source code
│   └── public/        # Static assets
└── docker-compose.yml  # Docker orchestration
```

## Technology Stack

- **Frontend**: React 19
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL 15
- **Storage**: Azure Blob Storage
- **Authentication**: JWT (mock for PoC)

## Development

### Running Tests

```bash
cd api
pytest tests/
```

### API Documentation

Once the API is running, interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Notes

- This is a Proof of Concept (PoC) implementation
- JWT authentication is mocked for demonstration purposes
- For production use, implement proper authentication, RBAC, encryption, and HIPAA compliance measures as outlined in the technical design document
