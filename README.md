# RAG Document Chat API

A powerful Retrieval-Augmented Generation (RAG) API service that enables intelligent chat with your documents using Ollama LLM and LEANN vector database.

## Features

- **Document Upload & Management**: Upload PDF, TXT, and Markdown documents (Markdown preferred for best results)
- **Vector Indexing**: Automatic document indexing using LEANN vector database
- **RAG Chat**: Chat with your documents using context-aware responses powered by Ollama
- **Multi-Document Support**: Query across multiple documents simultaneously
- **Chat Sessions**: Persistent chat sessions with conversation history
- **JWT Authentication**: Secure API access with user authentication
- **Background Processing**: Asynchronous document indexing for optimal performance

## Architecture

- **FastAPI**: Modern, fast web framework for building APIs
- **LEANN**: Efficient vector database for semantic search
- **Ollama**: Local LLM inference (default: qwen2.5:7b-instruct)
- **SQLAlchemy**: Database ORM for SQLite
- **PyMuPDF**: PDF text extraction

## Installation

### 1. Virtual Environment

The service uses a dedicated virtual environment:

```bash
# Create virtual environment
python3 -m venv /home/pi/api_rag_env

# Activate virtual environment
source /home/pi/api_rag_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Copy the example environment file and configure:

```bash
cp .env.example .env
nano .env
```

Key configuration options:
- `SECRET_KEY`: JWT secret (generate with `openssl rand -hex 32`)
- `OLLAMA_BASE_URL`: Ollama server URL (default: http://localhost:11434)
- `OLLAMA_MODEL`: LLM model to use (default: qwen2.5:7b-instruct)
- `LEANN_INDEX_PATH`: Path for vector indices
- `DATABASE_URL`: SQLite database path

### 3. Create Admin User

```bash
python3 create_admin.py
```

### 4. Run the Service

#### Development Mode

```bash
source /home/pi/api_rag_env/bin/activate
python app/main.py
```

#### Production Mode (Supervisor)

```bash
sudo cp supervisor.conf /etc/supervisor/conf.d/api_rag.conf
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start api_rag
```

## API Endpoints

### Base URL
- Local: `http://localhost:6956`
- Public: `https://api.pibico.es/rag/` (via nginx proxy)

### Documentation
- Swagger UI: `/api/docs`
- ReDoc: `/api/redoc`

### Authentication

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "user",
  "email": "user@example.com",
  "password": "securepassword"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=user&password=securepassword
```

Response:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### Documents

#### Upload Document
```http
POST /api/documents/upload
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: <document.md>
title: "My Document"
```

#### List Documents
```http
GET /api/documents/
Authorization: Bearer {token}
```

#### Get Document
```http
GET /api/documents/{document_id}
Authorization: Bearer {token}
```

#### Delete Document
```http
DELETE /api/documents/{document_id}
Authorization: Bearer {token}
```

### Chat

#### Create Chat Session
```http
POST /api/chat/sessions
Authorization: Bearer {token}
Content-Type: application/json

{
  "document_id": 1,
  "title": "Chat about document"
}
```

For multiple documents:
```json
{
  "document_ids": [1, 2, 3],
  "title": "Multi-document chat"
}
```

#### List Chat Sessions
```http
GET /api/chat/sessions
Authorization: Bearer {token}
```

#### Get Chat Session
```http
GET /api/chat/sessions/{session_id}
Authorization: Bearer {token}
```

#### Query Document (RAG)
```http
POST /api/chat/query
Authorization: Bearer {token}
Content-Type: application/json

{
  "session_id": 1,
  "query": "What is this document about?",
  "top_k": 5
}
```

Response:
```json
{
  "answer": "Based on the document...",
  "context_chunks": ["Relevant chunk 1", "Relevant chunk 2"],
  "session_id": 1,
  "message_id": 123,
  "query_timestamp": "2025-10-18T10:00:00",
  "response_timestamp": "2025-10-18T10:00:03",
  "elapsed_time": 3.14
}
```

#### Delete Chat Session
```http
DELETE /api/chat/sessions/{session_id}
Authorization: Bearer {token}
```

## Integration with Other Services

### Docling (PDF to Markdown Conversion)

Convert PDFs to Markdown for better RAG performance:

```bash
# Use Docling API to convert PDF to MD
curl -X POST "https://api.pibico.es/transform/convert" \
  -F "file=@document.pdf" \
  -F "output_format=markdown" \
  -o document.md

# Then upload to RAG API
curl -X POST "https://api.pibico.es/rag/api/documents/upload" \
  -H "Authorization: Bearer {token}" \
  -F "file=@document.md" \
  -F "title=My Document"
```

### PaddleOCR (OCR Processing)

Extract text from images before uploading:

```bash
# Use PaddleOCR API for OCR
curl -X POST "https://api.pibico.es/aiocr/ocr" \
  -F "file=@scan.jpg" \
  > extracted.txt

# Upload to RAG API
curl -X POST "https://api.pibico.es/rag/api/documents/upload" \
  -H "Authorization: Bearer {token}" \
  -F "file=@extracted.txt" \
  -F "title=Scanned Document"
```

## Usage Tips

1. **Markdown Preferred**: Upload documents in Markdown format for best chunking and retrieval
2. **Document Size**: Keep documents under 100MB for optimal performance
3. **Chunk Size**: Default 1000 characters with 200 character overlap
4. **Top K Results**: Default 5 most relevant chunks per query (configurable 1-20)
5. **Multi-Document**: Query across multiple related documents for comprehensive answers
6. **Context Window**: Last 5 messages included in conversation history

## Monitoring

Check service status:
```bash
sudo supervisorctl status api_rag
```

View logs:
```bash
tail -f logs/api_rag.log
```

## Troubleshooting

### Index Build Fails
- Check document format is supported (PDF, TXT, MD)
- Verify LEANN is properly installed
- Check disk space in data/leann_index directory

### Ollama Connection Error
- Verify Ollama is running: `ollama list`
- Check OLLAMA_BASE_URL in .env
- Test connection: `curl http://localhost:11434/api/tags`

### Database Errors
- Check database file permissions
- Verify DATABASE_URL path exists
- Run migrations if schema changed

## Development

Run tests:
```bash
pytest tests/
```

Format code:
```bash
black app/
```

Type checking:
```bash
mypy app/
```

## License

MIT License

## Support

For issues and questions:
- GitHub: https://github.com/your-org/api-rag
- Email: support@pibico.es
