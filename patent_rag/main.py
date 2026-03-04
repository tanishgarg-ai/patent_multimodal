import time
import logging
import json
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

def main():
    logger.info("Initializing Patent Prior Art Multimodal RAG System...")
    
    # 1. Data Ingestion
    ingestion = DataIngestionPipeline()
    documents = ingestion.ingest_all()
    
    # 2. Document Processing
    chunker = PatentChunker(chunk_size_tokens=500, chunk_overlap_tokens=100)
    chunks = chunker.chunk_documents(documents)
    
    # 3. Embedding Pipeline
    embedder = EmbeddingPipeline(model_name="all-MiniLM-L6-v2")
    
    # 4. Vector Store
    vector_store = PatentVectorStore(embedder=embedder)
    # For demo purposes, we can clear the collection or just add on top. 
    # Usually we check if it's already indexed. Adding for demo.
    vector_store.add_chunks(chunks, batch_size=32)
    
    # 5. Retrieval Engine
    retriever = PatentRetrievalEngine(vector_store=vector_store)
    
    # 6. Novelty Analyzer (Reasoning)
    analyzer = NoveltyAnalyzer()
    
    # Example Workflow Execution
    invention_desc = "An AI-based drone navigation system using LiDAR sensors and deep learning for real-time obstacle avoidance."
    logger.info(f"\n[QUERY] Testing Invention Description: {invention_desc}")
    
    # Time retrieval
    start_time = time.time()
    results = retriever.retrieve_similar_documents(invention_desc, top_k=2)
    latency = time.time() - start_time
    logger.info(f"Retrieval latency: {latency:.2f} seconds")
    
    # Generate Novelty Analysis
    analysis_report = analyzer.analyze(invention_desc, results)
    
    print("\n" + "="*50)
    print("NOVELTY ANALYSIS REPORT")
    print("="*50)
    print(analysis_report)
    print("="*50)
    
    # 7. Evaluation & Visualization
    evaluator = EvaluationModule()
    # Plotting similarity distribution of retrieved items
    all_retrieved = results['similar_patents'] + results['similar_papers'] + results['similar_claims']
    evaluator.plot_similarity_distribution(all_retrieved, output_path="similarity_dist.png")
    evaluator.plot_response_latency([latency], output_path="latency.png")

if __name__ == "__main__":
    main()
