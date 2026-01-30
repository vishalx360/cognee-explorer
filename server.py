"""
Cognee Web Server - FastAPI backend for the Cognee web interface
"""

import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

import cognee
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Neo4j configuration from environment
NEO4J_URL = os.getenv("GRAPH_DATABASE_URL", "bolt://localhost:7687")
NEO4J_USER = os.getenv("GRAPH_DATABASE_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("GRAPH_DATABASE_PASSWORD", "password123")


def get_neo4j_driver():
    """Get a Neo4j driver using environment configuration."""
    from neo4j import GraphDatabase
    return GraphDatabase.driver(NEO4J_URL, auth=(NEO4J_USER, NEO4J_PASSWORD))


class AddTextRequest(BaseModel):
    text: str


class SearchRequest(BaseModel):
    query: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize Cognee on startup."""
    print("Initializing Cognee...")
    yield
    print("Shutting down...")


app = FastAPI(title="Cognee Web Interface", lifespan=lifespan)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def serve_index():
    """Serve the HTML interface."""
    return FileResponse("index.html")


@app.post("/api/add")
async def add_text(request: AddTextRequest):
    """Add text to the Cognee knowledge base."""
    try:
        await cognee.add(request.text)
        return {"status": "success", "message": "Text added to knowledge base"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/cognify")
async def cognify():
    """Process the knowledge base to build the knowledge graph."""
    try:
        await cognee.cognify()
        return {"status": "success", "message": "Knowledge graph built successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/search")
async def search(request: SearchRequest):
    """Search the knowledge base."""
    try:
        results = await cognee.search(request.query)

        # Parse the results
        answers = []
        if results:
            for result in results:
                if isinstance(result, str):
                    answers.append(result)
                elif isinstance(result, dict):
                    search_result = result.get('search_result', [])
                    if isinstance(search_result, list):
                        answers.extend(search_result)
                    else:
                        answers.append(str(search_result))
                elif hasattr(result, 'text'):
                    answers.append(result.text)
                else:
                    answers.append(str(result))

        return {"status": "success", "results": answers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/reset")
async def reset():
    """Reset the knowledge base."""
    try:
        await cognee.prune.prune_data()
        await cognee.prune.prune_system(metadata=True)
        return {"status": "success", "message": "Knowledge base reset"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/api/documents")
async def list_documents():
    """List all documents in the knowledge base."""
    try:
        driver = get_neo4j_driver()
        documents = []
        with driver.session() as session:
            result = session.run('''
                MATCH (c:DocumentChunk)-[:is_part_of]->(d:TextDocument)
                WHERE c.chunk_index = 0
                RETURN d.id as id, d.name as name, d.created_at as created_at,
                       substring(c.text, 0, 200) as preview
                ORDER BY d.created_at DESC
            ''')
            for record in result:
                preview = (record['preview'] or '').replace('\n', ' ').strip()
                documents.append({
                    "id": record["id"],
                    "name": record["name"],
                    "preview": preview[:150] + "..." if len(preview) > 150 else preview,
                    "created_at": record["created_at"]
                })

        driver.close()
        return {"documents": documents}
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=f"{str(e)}\n{traceback.format_exc()}")


@app.delete("/api/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document and its chunks from the knowledge base."""
    try:
        driver = get_neo4j_driver()
        with driver.session() as session:
            # Delete chunks associated with this document
            session.run('''
                MATCH (c:DocumentChunk)-[:is_part_of]->(d:TextDocument {id: $doc_id})
                DETACH DELETE c
            ''', doc_id=doc_id)

            # Delete the document itself
            session.run('''
                MATCH (d:TextDocument {id: $doc_id})
                DETACH DELETE d
            ''', doc_id=doc_id)

            # Also delete any TextSummary connected to these chunks
            session.run('''
                MATCH (s:TextSummary)
                WHERE NOT EXISTS { MATCH (s)<-[:has_summary]-() }
                DETACH DELETE s
            ''')

        driver.close()
        return {"status": "success", "message": "Document deleted"}
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=f"{str(e)}\n{traceback.format_exc()}")


@app.get("/api/graph-data")
async def get_graph_data_api():
    """Fetch graph data from Neo4j for visualization."""
    try:
        driver = get_neo4j_driver()
        nodes = []
        edges = []

        with driver.session() as session:
            # Get all nodes
            result = session.run("MATCH (n) RETURN n, labels(n) as labels LIMIT 500")
            for record in result:
                node = record["n"]
                labels = record["labels"]
                node_type = next((l for l in labels if l != "__Node__"), "Unknown")

                props = dict(node)
                label = props.get("name", props.get("text", str(props.get("id", ""))[:30]))
                if label and len(label) > 40:
                    label = label[:40] + "..."

                nodes.append({
                    "id": props.get("id", str(node.element_id)),
                    "label": label or node_type,
                    "type": node_type,
                    "title": f"Type: {node_type}\\n{label}"
                })

            # Get all relationships
            result = session.run("MATCH (a)-[r]->(b) RETURN a.id as from_id, b.id as to_id, type(r) as rel_type LIMIT 1000")
            for record in result:
                edges.append({
                    "from": record["from_id"],
                    "to": record["to_id"],
                    "label": record["rel_type"],
                    "title": record["rel_type"]
                })

        driver.close()
        return {"nodes": nodes, "edges": edges}
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=f"{str(e)}\n{traceback.format_exc()}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
