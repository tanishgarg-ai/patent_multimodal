import time
import logging
import json
import os
from dotenv import load_dotenv
from data_ingestion import DataIngestionPipeline
from document_processor import PatentChunker
from embedding_pipeline import EmbeddingPipeline
from vector_store import PatentVectorStore
from retrieval_engine import PatentRetrievalEngine
from novelty_analyzer import NoveltyAnalyzer
from multimodal_module import MultimodalModule
from evaluation import EvaluationModule

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def main():
    logger.info("Initializing Patent Prior Art Multimodal RAG System...")
    
    # Example Workflow Execution
    # invention_desc = "An AI-based drone navigation system using LiDAR sensors and deep learning for real-time obstacle avoidance."
    invention_desc = "light bulb with smart phone control."
    logger.info(f"\n[QUERY] Testing Invention Description: {invention_desc}")

    # 1. Data Ingestion from Web
    # Fetching relevant documents from Semantic Scholar and PatentsView
    ingestion = DataIngestionPipeline(
        semantic_scholar_api_key=os.getenv("SEMANTIC_SCHOLAR_API_KEY"),
        uspto_api_key=os.getenv("USPTO_API_KEY"),
        google_project_id=os.getenv("GOOGLE_CLOUD_PROJECT")
    )
    logger.info("Fetching real-world documents from the web...")
    documents = ingestion.ingest_from_web(invention_desc, limit=5)
    
    if not documents:
        logger.warning("No documents found on the web. Falling back to local sample data.")
        documents = ingestion.ingest_all()
    
    # 2. Document Processing
    chunker = PatentChunker(chunk_size_tokens=500, chunk_overlap_tokens=100)
    chunks = chunker.chunk_documents(documents)
    
    # 3. Embedding Pipeline
    embedder = EmbeddingPipeline(model_name="all-MiniLM-L6-v2")
    
    # 4. Vector Store
    vector_store = PatentVectorStore(embedder=embedder)
    # Clear collection for a fresh search result each time for this demo
    try:
        vector_store.client.delete_collection(vector_store.collection_name)
        vector_store.collection = vector_store.client.create_collection(
            name=vector_store.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    except:
        pass
        
    vector_store.add_chunks(chunks, batch_size=32)
    
    # 5. Retrieval Engine
    retriever = PatentRetrievalEngine(vector_store=vector_store)
    
    # 6. Novelty Analyzer (Reasoning)
    analyzer = NoveltyAnalyzer()
    
    # Time retrieval
    start_time = time.time()
    results = retriever.retrieve_similar_documents(invention_desc, top_k=5)
    latency = time.time() - start_time
    logger.info(f"Retrieval latency: {latency:.2f} seconds")
    
    # Generate Novelty Analysis
    analysis_report = analyzer.analyze(invention_desc, results)
    
    print("\n" + "="*50)
    print("REAL-WORLD NOVELTY ANALYSIS REPORT")
    print("="*50)
    print(analysis_report)
    print("="*50)
    
    # 7. Evaluation & Visualization
    evaluator = EvaluationModule()
    all_retrieved = results['similar_patents'] + results['similar_papers'] + results['similar_claims']
    if all_retrieved:
        evaluator.plot_similarity_distribution(all_retrieved, output_path="similarity_dist.png")
    evaluator.plot_response_latency([latency], output_path="latency.png")

if __name__ == "__main__":
    main()
