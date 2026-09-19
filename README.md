# Algo Pal

Algo Pal is a FastAPI-based DSA mentoring chatbot with an HTML chat interface, Azure OpenAI, MongoDB session storage, and optional Qdrant semantic search.

## Requirements

- Python 3.11 or newer
- An Azure OpenAI deployment for chat
- An Azure OpenAI embedding deployment for semantic search
- MongoDB running at `mongodb://localhost:27017` (required for sessions)
- Qdrant running at `http://localhost:6333` (optional; vector search is disabled when unavailable)

## Setup

From the repository root, create and activate the virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

Create a `.env` file in the repository root:

```env
ENVIRONMENT=development
DEBUG=true
HOST=0.0.0.0
PORT=8000

AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your-chat-deployment
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=your-embedding-deployment
AZURE_OPENAI_API_VERSION=2023-05-15

MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=algo_pal
MONGODB_COLLECTION=chat_sessions

QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=algo_pal_graph
# QDRANT_API_KEY=your-qdrant-api-key
```

Do not commit `.env` or real API keys.

## Run with Uvicorn

Activate the virtual environment, then start the development server:

```bash
source .venv/bin/activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Alternatively, use the configured values from `.env` through the application entry point:

```bash
python main.py
```

Open the application at <http://localhost:8000>.

Useful endpoints:

- Web app: <http://localhost:8000>
- Health check: <http://localhost:8000/health>
- Swagger API docs: <http://localhost:8000/api/docs>
- ReDoc API docs: <http://localhost:8000/api/redoc>

## Troubleshooting

### `ImportError: cannot import name 'Qdrant'`

The project uses the standalone `langchain-qdrant` integration. Refresh dependencies inside the active virtual environment:

```bash
source .venv/bin/activate
python -m pip install -U langchain-qdrant
```

### `python: command not found`

Use the virtual environment explicitly:

```bash
.venv/bin/python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### MongoDB connection errors

Start MongoDB locally or set `MONGODB_URI` in `.env` to a reachable MongoDB instance. Session creation and chat persistence require MongoDB.
