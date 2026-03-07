from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import os
import tempfile
import uuid

from pdf_utils import PDFProcessor
from document_processor import PatentChunker

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


from fastapi.staticfiles import StaticFiles

# Ensure static directory exists
os.makedirs("static/pdfs", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/api/upload")
async def upload_document(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        if not file.filename.endswith(".pdf"):
            results.append({"filename": file.filename, "status": "error", "message": "Only PDF files are supported"})
            continue
            
        logger.info(f"Received upload request for file: {file.filename}")
        
        patent_id = str(uuid.uuid4())
        # Save the file permanently to static/pdfs
        permanent_path = f"static/pdfs/{patent_id}.pdf"
        
        try:
            with open(permanent_path, 'wb') as f:
                f.write(await file.read())

            # Process the PDF using pdf_utils
            processor = PDFProcessor()
            description, claims = processor.process_pdf(permanent_path)

            if not description and not claims:
                results.append({"filename": file.filename, "status": "error", "message": "Could not extract text from the PDF. It might be image-only or corrupted."})
                # Optional: Delete the file if we can't process it correctly to save space, but keeping it might be useful for manual review
                continue
            
            # Determine title from filename (strip extension)
            title = os.path.splitext(file.filename)[0]
            
            # The URL frontend can use to access this PDF
            static_pdf_url = f"http://localhost:8000/static/pdfs/{patent_id}.pdf"

            document = {
                "doc_type": "patent",
                "patent_id": patent_id,
                "title": title,
                "abstract": description[:500] + "..." if len(description) > 500 else description,
                "claims": claims,
                "description": description,
                "publication_date": "2026-01-01",  # Dummy or could extract from text
                "classification": "UNKNOWN",
                "pdf_url": static_pdf_url,
                "image_paths": []
            }

            # Chunk the document
            chunker = PatentChunker()
            chunks = chunker.chunk_documents([document])
            
            if not chunks:
                results.append({"filename": file.filename, "status": "error", "message": "Failed to create chunks from document"})
                continue

            # Add chunks to vector store
            if vector_store:
                vector_store.add_chunks(chunks)
                logger.info(f"Successfully processed and stored {len(chunks)} chunks for {file.filename}")
                results.append({
                    "filename": file.filename, 
                    "status": "success", 
                    "message": f"Successfully processed {file.filename}", 
                    "chunks_added": len(chunks), 
                    "patent_id": patent_id,
                    "pdf_url": static_pdf_url
                })
            else:
                results.append({"filename": file.filename, "status": "error", "message": "Vector store is not initialized"})
                
        except Exception as e:
            logger.error(f"Error processing upload for {file.filename}: {e}")
            results.append({"filename": file.filename, "status": "error", "message": f"Error processing document: {str(e)}"})
            
    return {"results": results}


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Patent Prior Art RAG API is running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
