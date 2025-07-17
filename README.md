# Document-Based Chatbot with LangGraph

A production-ready document-based chatbot system built with clean architecture principles, featuring Streamlit UI, Milvus vector database, OpenAI embeddings, and LangGraph for intelligent search and response generation.

## Architecture

This project follows clean architecture principles with the following layers:

- **Domain**: Core business entities (`Document`, `DocumentChunk`)
- **Ports**: Interfaces for repository and usecase layers
- **Repository**: Milvus vector database implementation for document chunks
- **Usecase**: Business logic for document processing and search
- **Controller**: FastAPI REST API endpoints
- **Infrastructure**: OpenAI service, document processor, and LangGraph chat

## Features

- ✅ Upload and process PDF documents
- ✅ Automatic text extraction and chunking
- ✅ Vector embeddings using OpenAI text-embedding-3-small
- ✅ Intelligent search with LangGraph workflow
- ✅ Memory and context across chat sessions
- ✅ Iterative query refinement
- ✅ Clean architecture with proper separation of concerns
- ✅ RESTful API with FastAPI
- ✅ Modern UI with Streamlit
- ✅ Vector database with Milvus
- ✅ Production-ready structure

## LangGraph Workflow

The system uses LangGraph to implement an intelligent search workflow:

1. **Receive user question**
2. **Perform similarity search** in vector database
3. **Evaluate if results contain answer**
4. **Generate answer** if sufficient information found
5. **Modify query and search again** if needed (up to 3 attempts)
6. **Maintain memory** across interactions

## Setup

### Prerequisites

- Python 3.9+
- Poetry (package manager)
- Milvus server running
- OpenAI API key

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   poetry install
   ```

3. Set up environment variables (create `.env` file):
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   MILVUS_HOST=localhost
   MILVUS_PORT=19530
   MILVUS_DB_NAME=default
   ```

4. Start Milvus server (using Docker):
   ```bash
   docker run -d --name milvus_standalone -p 19530:19530 -p 9091:9091 milvusdb/milvus:latest standalone
   ```

### Running the Application

1. Start the FastAPI backend:
   ```bash
   poetry run python document_app.py
   ```

2. Start the Streamlit UI (in a new terminal):
   ```bash
   poetry run streamlit run document_streamlit_app.py
   ```

3. Access the application:
   - Streamlit UI: http://localhost:8501
   - API Documentation: http://localhost:8000/docs

## API Endpoints

- `POST /documents/upload` - Upload and process PDF document
- `POST /chat` - Chat with document system using LangGraph
- `GET /documents` - List all uploaded documents
- `DELETE /documents/{document_id}` - Delete document
- `GET /health` - Health check

## Features

### Document Processing
- PDF text extraction and chunking
- Automatic embedding generation
- Vector storage in Milvus
- Metadata preservation

### Intelligent Chat
- LangGraph-powered search workflow
- Context-aware responses
- Query refinement and iteration
- Session memory and persistence

### Document Management
- Upload PDF documents
- View document information
- Delete documents and chunks
- Monitor processing status

## Project Structure

```
├── src/
│   ├── domain/           # Business entities (Document, DocumentChunk)
│   ├── ports/            # Interfaces
│   ├── repository/       # Data access layer (Milvus)
│   ├── usecase/          # Business logic
│   ├── controller/       # API endpoints
│   └── infrastructure/   # External services (OpenAI, LangGraph)
├── tests/                # Unit and integration tests
├── data/                 # Data files
├── docs/                 # Documentation
├── document_app.py       # Document chatbot entry point
├── document_streamlit_app.py # Streamlit UI for documents
├── main.py              # FAQ chatbot entry point (legacy)
├── streamlit_app.py     # FAQ chatbot UI (legacy)
└── pyproject.toml       # Poetry configuration
```

## Development

### Adding New Features

1. Define domain entities in `src/domain/`
2. Create ports (interfaces) in `src/ports/`
3. Implement repository in `src/repository/`
4. Add business logic in `src/usecase/`
5. Create API endpoints in `src/controller/`
6. Update UI in `document_streamlit_app.py`

### Testing

Run tests with:
```bash
poetry run pytest
```

## Production Deployment

For production deployment:

1. Use proper dependency injection container
2. Add authentication and authorization
3. Implement proper error handling and logging
4. Add monitoring and health checks
5. Use environment-specific configurations
6. Add comprehensive test coverage
7. Set up proper OpenAI API key management
8. Configure Milvus for production use
9. Implement document versioning and backup

## Contributing

1. Follow clean architecture principles
2. Write tests for new features
3. Update documentation
4. Use type hints throughout
5. Follow PEP 8 style guidelines
 
