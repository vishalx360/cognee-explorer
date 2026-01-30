# Cognee Explorer

A web interface for [Cognee](https://github.com/topoteretes/cognee) - an AI memory framework that builds knowledge graphs from unstructured data.

## Features

- **Add Data**: Drop files or paste text to add to the knowledge base
- **Build Graph**: Process data into a searchable knowledge graph
- **Search**: Query your data using natural language
- **Visualize**: Interactive graph visualization with Neo4j
- **Manage**: View and delete individual documents

## Prerequisites

- Python 3.10+
- Neo4j (local or Docker)
- OpenAI-compatible LLM API (or local LLM)

## Quick Start

### 1. Clone and Install

```bash
git clone https://github.com/yourusername/cognee-explorer.git
cd cognee-explorer
pip install -r requirements.txt
```

### 2. Start Neo4j

Using Docker:
```bash
docker run -d \
  --name cognee-neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password123 \
  neo4j:5-community
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys and Neo4j credentials
```

### 4. Run

```bash
python server.py
```

Open http://localhost:8000

## Configuration

See `.env.example` for all configuration options:

| Variable | Description |
|----------|-------------|
| `LLM_PROVIDER` | LLM provider (openai, anthropic, etc.) |
| `LLM_MODEL` | Model name |
| `LLM_ENDPOINT` | API endpoint URL |
| `LLM_API_KEY` | API key |
| `EMBEDDING_PROVIDER` | Embedding provider (fastembed for local) |
| `GRAPH_DATABASE_PROVIDER` | Graph DB (neo4j) |
| `GRAPH_DATABASE_URL` | Neo4j bolt URL |
| `GRAPH_DATABASE_USERNAME` | Neo4j username |
| `GRAPH_DATABASE_PASSWORD` | Neo4j password |

## Usage

1. **Add Data**: Drag & drop files (.txt, .md, .json, .csv, .pdf) or paste text
2. **Build Graph**: Click "Build Graph" to process data into a knowledge graph
3. **Search**: Ask questions about your data
4. **View Graph**: See the knowledge graph visualization on the right panel
5. **Manage**: Delete documents from the Documents section

## Project Structure

```
cognee-explorer/
├── server.py           # FastAPI backend
├── index.html          # Web interface
├── requirements.txt    # Python dependencies
├── .env.example        # Example configuration
└── cognee_example.py   # Standalone CLI example
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Web interface |
| POST | `/api/add` | Add text to knowledge base |
| POST | `/api/cognify` | Build knowledge graph |
| POST | `/api/search` | Search the knowledge base |
| POST | `/api/reset` | Reset all data |
| GET | `/api/documents` | List all documents |
| DELETE | `/api/documents/{id}` | Delete a document |
| GET | `/api/graph-data` | Get graph for visualization |
| GET | `/api/health` | Health check |

## License

MIT

## Credits

Built with [Cognee](https://github.com/topoteretes/cognee) - Memory for AI Agents
