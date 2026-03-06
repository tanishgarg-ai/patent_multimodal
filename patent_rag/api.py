from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

from embedding_pipeline import EmbeddingPipeline
from vector_store import PatentVectorStore
from retrieval_engine import PatentRetrievalEngine
from novelty_analyzer import NoveltyAnalyzer

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load env
load_dotenv()

app = FastAPI(title="Patent Prior Art RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for RAG components
embedder = None
vector_store = None
retriever = None
analyzer = None


@app.on_event("startup")
async def startup_event():
    global embedder, vector_store, retriever, analyzer
    logger.info("Initializing Patent RAG API components...")

    embedder = EmbeddingPipeline(model_name="all-MiniLM-L6-v2")
    vector_store = PatentVectorStore(embedder=embedder)
    retriever = PatentRetrievalEngine(vector_store=vector_store)
    analyzer = NoveltyAnalyzer()

    logger.info("Patent RAG API components loaded successfully.")


class QueryRequest(BaseModel):
    description: str
    diagram: Optional[str] = None


class QueryResponse(BaseModel):
    analysis_report: str
    patents: List[Dict[str, Any]]
    papers: List[Dict[str, Any]]
    similarity_scores: List[float]
    novelty_assessment: Dict[str, Any]
    graph_data: Dict[str, Any]


@app.post("/api/analyze", response_model=QueryResponse)
async def analyze_invention(req: QueryRequest):
    if not req.description:
        raise HTTPException(status_code=400, detail="Invention description is required")

    try:
        # Retrieve documents
        results = retriever.retrieve_similar_documents(req.description, top_k=5)

        # Analyze novelty
        report = analyzer.analyze(req.description, results)

        patents = []
        for doc in results.get("similar_patents", []) + results.get("similar_claims", []):
            patent_item = doc.copy()
            # Ensure metadata fields are flattened or accessible if needed
            # The frontend expects certain fields
            patents.append({
                "id": doc.get("id"),
                "content": doc.get("content"),
                "similarity_score": doc.get("similarity_score"),
                "title": doc["metadata"].get("title") or doc["metadata"].get("parent_document_id"),
                "patent_number": doc["metadata"].get("parent_document_id"),
                "abstract": doc.get("content"),  # or metadata abstract
                "pdf_url": doc["metadata"].get("pdf_url", ""),
                "metadata": doc["metadata"]
            })

        papers = results.get("similar_papers", [])
        similarity_scores = [doc.get("similarity_score", 0.0) for doc in
                             (results.get("similar_patents", []) + results.get("similar_claims", []) + papers)]

        return QueryResponse(
            analysis_report=report,
            patents=patents,
            papers=papers,
            similarity_scores=similarity_scores,
            novelty_assessment={"risk_level": "UNKNOWN", "details": "See analysis_report"},
            graph_data={"nodes": [], "edges": []}
        )
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Patent Prior Art RAG API is running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
